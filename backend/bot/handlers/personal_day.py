from datetime import date

from aiogram import F, Router, flags
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from django.utils.timezone import now

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.services.numerology import get_personal_day_number
from bot.text_templates.personal_day import moon_phases, personal_day_messages
from core.choices import Actions
from core.models import Client, ClientAction

router = Router()


@router.message(F.text == '📆 Твой личный день')
@flags.with_client
async def personal_day_preview(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
            client.genderize(
                '📆 Твой личный день\n\n'
                'У каждого дня есть свой код.\n'
                'Я могу расшифровать твой — но сначала ты {gender:должен,должна} появиться.\n\n'
                'Зарегистрируйся, и я расскажу, куда ведёт твой день.',
            ),
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
            client.genderize(
                '📆 Твой личный день\n\n'
                'Этот день говорит на твоём языке.\n'
                'Хочешь понять, с какой энергией ты {gender:проснулся,проснулась} сегодня?\n\n'
                'Я собрала всё: цифры, звёзды, внутренние ритмы.\n'
                'Открой — и проживи этот день осознанно.',
            ),
            reply_markup=one_button_keyboard(
                text='🌞 Посмотреть прогноз дня',
                callback_data='personal_day',
            ),
        )
    else:
        await msg.answer(
            client.genderize(
                '📆 Твой личный день\n\n'
                'Твои дни больше не звучат в тишине.\n'
                'Ты уже {gender:слышал,слышала}, как день может быть направляющим.\n\n'
                'Хочешь продолжить? Тогда дай себе доступ к себе.',
            ),
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Разблокировать прогнозы',
            ),
        )


@router.callback_query(F.data == 'personal_day')
@flags.with_client
async def personal_day(query: CallbackQuery, client: Client):
    phase = moon_phases[date.today().strftime('%d.%m.%Y')]
    number = get_personal_day_number(client.birth.date())
    await query.message.edit_text(
        personal_day_messages[phase][number],
    )

    if not client.subscription_is_active():
        await query.message.answer(
            client.genderize(
                '<b>Ты {gender:почувствовал,почуствовала}, как это работает.</b>\n'
                'Каждый день — как подсказка, куда смотреть и что делать.\n'
                'Но это было лишь знакомство.\n'
                '<b>Хочешь, чтобы я приходила к тебе каждый день — с твоим прогнозом?\n'
                'Оформи подписку — и не теряй связь с собой.</b>',
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_to_subscription_plans_kb(
                text='💫 Получить доступ к личному дню',
            ),
        )

    await ClientAction.objects.aget_or_create(
        client=client,
        action=Actions.PERSONAL_DAY,
        date__date=now().date(),
    )
