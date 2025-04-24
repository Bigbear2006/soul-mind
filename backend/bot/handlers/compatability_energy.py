from datetime import datetime

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    compatability_energy_kb,
    get_to_registration_kb,
    get_to_subscription_plans_kb,
    show_connection_depth,
)
from bot.states import CompatabilityEnergyState
from bot.templates.compatability_energy import get_compatability_energy_text
from core.models import Actions, Client

# TODO: ограничить количество использований кнопки

router = Router()


@router.message(F.text == '💞 Энергия вашей совместимости')
@flags.with_client
async def compatability_energy(
    msg: Message, state: FSMContext, client: Client
):
    if not client.is_registered():
        await msg.answer(
            'Ты хочешь понять вас,\n'
            'но ещё не заглянул(а) в себя?\n\n'
            'Пройди регистрацию — и я покажу, как сплетается ваша энергия.',
            reply_markup=get_to_registration_kb(),
        )
        return

    if client.action_limit_exceed(Actions.COMPATABILITY_ENERGY):
        await msg.answer(
            'Твоя энергия не ограничена тремя людьми.\n'
            'Каждая новая связь — это отражение тебя.\n\n'
            'Разблокируй ещё совместимости\n\n'
            '🔹 1 совместимость → 159 ₽ или 250 астробаллов\n'
            '🔹 3 совместимости → 399 ₽ или 650 астробаллов\n'
            '🔹 VIP-анализ совместимости\n\n'
            'Ты готов(а) к настоящей глубине?\n'
            'Это больше, чем просто “подходите вы друг другу или нет”.\n'
            'Это разбор, после которого вы оба увидите себя иначе.\n\n'
            'Пара. Семья. Команда. Друзья.\n'
            'Выбирай формат — и ныряем вглубь.\n\n',
            reply_markup=show_connection_depth,
        )
        return

    if client.subscription_is_active():
        await state.set_state(CompatabilityEnergyState.connection_type)
        await msg.answer(
            'Случайных встреч не бывает.\n'
            'Я покажу, почему этот человек рядом — и чему вы учите друг друга.\n\n'
            'Ты готов(а) взглянуть на вашу связь по-настоящему?',
            reply_markup=compatability_energy_kb,
        )
    else:
        await msg.answer(
            'Связь, которую ты хочешь понять,\n'
            'не раскрывается за пару строк.\n\n'
            'Продолжи путь — и я покажу, что между вами на самом деле.',
            reply_markup=get_to_subscription_plans_kb(),
        )


@router.callback_query(
    F.data.in_(('together', 'like', 'past_lovers')),
    StateFilter(CompatabilityEnergyState.connection_type),
)
async def set_connection_type(query: CallbackQuery, state: FSMContext):
    await state.update_data(connection_type=query.data)
    await state.set_state(CompatabilityEnergyState.birth_date_2)
    await query.message.edit_text(
        '📆 Введи дату рождения человека, с которым проверяешь связь '
        'в формате ДД.ММ.ГГГГ.',
    )


@router.message(F.text, StateFilter(CompatabilityEnergyState.birth_date_2))
@flags.with_client
async def get_first_person_birth_date(
    msg: Message,
    state: FSMContext,
    client: Client,
):
    try:
        birth_date_2 = datetime.strptime(msg.text, '%d.%m.%Y')
    except ValueError:
        await msg.answer(
            'Некорректная дата. Попробуй еще раз',
        )
        return

    await msg.answer(
        get_compatability_energy_text(
            await state.get_value('connection_type'),
            client.birth.date(),
            birth_date_2,
        ),
        reply_markup=show_connection_depth,
    )
    await state.clear()
