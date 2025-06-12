from datetime import datetime

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.compatability_energy import (
    compatability_energy_kb,
    get_buy_compatability_kb,
    show_connection_depth,
    trial_usages_ended_kb,
)
from bot.keyboards.inline.vip_services import get_payment_choices_kb
from bot.services.compatability_energy import get_compatability_energy_text
from bot.settings import settings
from bot.states import CompatabilityEnergyState
from bot.text_templates.base import astropoints_not_enough
from bot.utils.formatters import compatability_plural, remaining_plural
from core.choices import Genders, SubscriptionPlans
from core.models import Actions, Client

router = Router()


@router.message(F.text == '💞 Энергия вашей совместимости')
@router.callback_query(F.data == 'compatability_energy')
@flags.with_client
async def compatability_energy(
    msg: Message | CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await client.refresh_limit(Actions.COMPATABILITY_ENERGY)
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )

    if not client.is_registered():
        await answer_func(
            client.genderize(
                'Ты хочешь понять вас,\n'
                'но ещё не {gender:заглянул,заглянула} в себя?\n\n'
                'Пройди регистрацию — и я покажу, как сплетается ваша энергия.',
            ),
            reply_markup=get_to_registration_kb(),
        )
        return

    remaining_usages = await client.get_remaining_usages(
        Actions.COMPATABILITY_ENERGY,
    )

    if remaining_usages <= 0:
        if client.has_trial():
            await answer_func(
                client.genderize(
                    'Ты уже {gender:посмотрел,посмотрела} две энергии. '
                    'И, возможно, {gender:почувствовал,почувствовала}, как это работает.\n'
                    'На тестовом доступе это максимум.'
                    'Но если ты хочешь увидеть глубже — у тебя есть два пути:',
                ),
                reply_markup=trial_usages_ended_kb,
            )
            return

        await answer_func(
            client.genderize(
                'Твоя энергия не ограничена тремя людьми.\n'
                'Каждая новая связь — это отражение тебя.\n\n'
                'Разблокируй ещё совместимости\n\n'
                '🔹 1 совместимость → 159 ₽ или 250 астробаллов\n'
                '🔹 3 совместимости → 399 ₽ или 650 астробаллов\n'
                '🔹 VIP-анализ совместимости\n\n'
                'Ты {gender:готов,готова} к настоящей глубине?\n'
                'Это больше, чем просто “подходите вы друг другу или нет”.\n'
                'Это разбор, после которого вы оба увидите себя иначе.\n\n'
                'Пара. Семья. Команда. Друзья.\n'
                'Выбирай формат — и ныряем вглубь.\n\n',
            ),
            reply_markup=get_buy_compatability_kb(),
        )
        return

    if client.subscription_is_active() or client.has_trial():
        remaining_usages_str = (
            f'* У тебя {remaining_plural(remaining_usages, Genders.FEMALE)} {remaining_usages} '
            f'{compatability_plural(remaining_usages)}'
            if client.subscription_plan != SubscriptionPlans.PREMIUM
            else ''
        )
        await state.set_state(CompatabilityEnergyState.connection_type)
        await answer_func(
            client.genderize(
                'Случайных встреч не бывает.\n'
                'Я покажу, почему этот человек рядом — и чему вы учите друг друга.\n\n'
                'Ты {gender:готов,готова} взглянуть на вашу связь по-настоящему?\n\n'
                f'{remaining_usages_str}',
            ),
            reply_markup=compatability_energy_kb,
        )
    else:
        await answer_func(
            'Связь, которую ты хочешь понять,\n'
            'не раскрывается за пару строк.\n\n'
            'Продолжи путь — и я покажу, что между вами на самом деле.',
            reply_markup=get_to_subscription_plans_kb(),
        )


###############################
### BUY EXTRA COMPATABILITY ###
###############################


@router.callback_query(F.data == 'buy_compatability_choices')
async def buy_compatability_choices(query: CallbackQuery):
    await query.message.edit_reply_markup(
        reply_markup=get_buy_compatability_kb(
            back_button_data='compatability_energy',
        ),
    )


@router.callback_query(F.data.startswith('buy_compatability'))
async def buy_compatability(query: CallbackQuery, state: FSMContext):
    buy_count = query.data.split(':')[1]
    await state.update_data(buy_count=buy_count)
    await state.set_state(CompatabilityEnergyState.payment_type)
    await query.message.edit_text(
        'Выбери тип оплаты',
        reply_markup=get_payment_choices_kb(
            '250 баллов' if buy_count == 'one' else '650 баллов',
            '159 ₽' if buy_count == 'one' else '399 ₽',
            back_button_data='buy_compatability_choices',
        ),
    )


@router.callback_query(
    F.data.in_(('astropoints', 'money')),
    StateFilter(CompatabilityEnergyState.payment_type),
)
@flags.with_client
async def choose_compatability_payment_type(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    buy_count = await state.get_value('buy_count')
    buy_count_str = '1' if buy_count == 'one' else '3'
    astropoints = 250 if buy_count == 'one' else 650
    money = 159 if buy_count == 'one' else 399

    if query.data == 'astropoints':
        if client.astropoints < astropoints:
            await query.message.edit_text(
                astropoints_not_enough,
                reply_markup=get_payment_choices_kb(
                    None,
                    '159 ₽' if buy_count == 'one' else '399 ₽',
                ),
            )
            return

        await client.add_extra_usages(
            action=Actions.COMPATABILITY_ENERGY,
            count=1 if await state.get_value('buy_count') == 'one' else 3,
        )
        client.astropoints -= astropoints
        await client.asave()

        remaining_usages = await client.get_remaining_usages(
            Actions.COMPATABILITY_ENERGY,
        )
        await query.message.edit_text(
            f'Теперь у тебя {remaining_usages} '
            f'{compatability_plural(remaining_usages)}!',
        )
        await state.clear()
    else:
        await query.message.answer_invoice(
            f'Дополнительные совместимости ({buy_count_str})',
            f'Дополнительные совместимости ({buy_count_str})',
            'extra_compatability',
            settings.CURRENCY,
            [LabeledPrice(label=settings.CURRENCY, amount=money * 100)],
            settings.PROVIDER_TOKEN,
        )
        await state.set_state(CompatabilityEnergyState.payment)


@router.pre_checkout_query(StateFilter(CompatabilityEnergyState.payment))
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@router.message(
    F.successful_payment,
    StateFilter(CompatabilityEnergyState.payment),
)
@flags.with_client
async def on_extra_compatability_buying(
    msg: Message,
    state: FSMContext,
    client: Client,
):
    await client.add_extra_usages(
        action=Actions.COMPATABILITY_ENERGY,
        count=1 if await state.get_value('buy_count') == 'one' else 3,
    )
    remaining_usages = await client.get_remaining_usages(
        Actions.COMPATABILITY_ENERGY,
    )
    await msg.answer(
        f'Теперь у тебя {remaining_usages} '
        f'{compatability_plural(remaining_usages)}!',
    )
    await state.clear()


##########################
### SHOW COMPATABILITY ###
##########################


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
            client,
            birth_date_2,
        ),
        reply_markup=show_connection_depth,
    )
    await client.spend_usage(Actions.COMPATABILITY_ENERGY)
    await state.clear()
