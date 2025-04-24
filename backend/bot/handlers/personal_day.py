from datetime import date

from aiogram import F, Router, flags
from aiogram.types import Message, CallbackQuery

from bot.calculations import calculate_number
from bot.keyboards.inline import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.templates.personal_day import moon_phases, personal_day_messages
from core.models import Client

router = Router()

# TODO: подсвечивать внутри бота, что Совет Вселенной или Твой личный  день не открыт


@router.message(F.text == '📆 Твой личный день')
@flags.with_client
async def personal_day_preview(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
            '📆 Твой личный день\n\n'
            'У каждого дня есть свой код.\n'
            'Я могу расшифровать твой — но сначала ты должен(на) появиться.\n\n'
            'Зарегистрируйся, и я расскажу, куда ведёт твой день.',
            reply_markup=get_to_registration_kb(
                text='🔓 Разблокировать доступ',
            ),
        )
    elif client.subscription_is_active():
        await msg.answer(
            '📆 Твой личный день\n\n'
            'Ты не случайно здесь и не случайно сейчас.\n'
            'Каждый день я расшифровываю твою энергию —\n'
            'на основе цифр, звёзд, ритма души.\n\n'
            'Открой и почувствуй, с чем ты входишь в этот день.',
            reply_markup=one_button_keyboard(
                text='🌞 Узнать свой прогноз',
                callback_data='personal_day',
            ),
        )
    elif client.has_trial():
        await msg.answer(
            '📆 Твой личный день\n\n'
            'Этот день говорит на твоём языке.\n'
            'Хочешь понять, с какой энергией ты проснулся(ась) сегодня?\n\n'
            'Я собрала всё: цифры, звёзды, внутренние ритмы.\n'
            'Открой — и проживи этот день осознанно.',
            reply_markup=one_button_keyboard(
                text='🌞 Посмотреть прогноз дня',
                callback_data='personal_day',
            ),
        )
    else:
        await msg.answer(
            '📆 Твой личный день\n\n'
            'Твои дни больше не звучат в тишине.\n'
            'Ты уже слышал(а), как день может быть направляющим.\n\n'
            'Хочешь продолжить? Тогда дай себе доступ к себе.',
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Разблокировать прогнозы',
            ),
        )


@router.callback_query(F.data == 'personal_day')
@flags.with_client
async def personal_day(query: CallbackQuery, client: Client):
    phase = moon_phases[
        date.today().strftime('%d.%m.%Y')
    ]  # for test: '10.05.2025'
    number = calculate_number(str(client.birth.date()), ())
    await query.message.edit_text(
        personal_day_messages[phase][number],
    )
