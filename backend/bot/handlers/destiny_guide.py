from datetime import date, timedelta

from aiogram import F, Router, flags
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from django.utils.timezone import now

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.destiny_guide import (
    destiny_guide_kb,
    to_destiny_guide_kb,
)
from bot.text_templates.destiny_guide import astro_events, important_days
from core.choices import Actions
from core.models import Client, ClientAction

router = Router()


@router.message(F.text == '🗺️ Путеводитель судьбы')
@router.callback_query(F.data == 'destiny_guide_intro')
@flags.with_client
async def destiny_guide_intro(msg: Message | CallbackQuery, client: Client):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )

    if not client.is_registered():
        await answer_func(
            client.genderize(
                '🗺️ Путеводитель судьбы\n\n'
                'Звёзды знают, где ты.\n'
                'Но пока ты не {gender:заявил,заявила} о себе — я не могу показать тебе их маршрут.\n\n'
                'Пройди регистрацию — и я дам тебе карту того, что приближается.',
            ),
            reply_markup=get_to_registration_kb(
                text='🔓 Разблокировать доступ',
            ),
        )
    elif client.subscription_is_active():
        await answer_func(
            '🗺️ Путеводитель судьбы\n\n'
            'Я держу руку на пульсе космоса —\n'
            'и каждый месяц собираю для тебя карту:\n'
            'когда начинать, когда наблюдать, когда беречь, а когда сиять.\n\n'
            'Астрособытия. Важные дни. Личное направление.',
            reply_markup=destiny_guide_kb,
        )
    elif client.has_trial():
        await answer_func(
            '🗺️ Путеводитель судьбы\n\n'
            'Ретрограды, затмения, важные транзиты —\n'
            'я собрала всё, что двигает пространство.\n'
            'Ты видишь главное. Остальное раскроется, если захочешь глубже.\n\n'
            'Хочешь знать, с какой энергией входит месяц?',
            reply_markup=destiny_guide_kb,
        )
    else:
        await answer_func(
            client.genderize(
                '🗺️ Путеводитель судьбы\n\n'
                'Ты видишь главное —\n'
                'ретрограды, затмения, ключевые движения неба.\n'
                'Этого уже достаточно, чтобы идти осознанно.\n'
                'Но я могу показать больше… когда ты будешь {gender:готов,готова}.\n\n'
                'P.S. Подписка откроет доступ к важным дням в твоих сферах.',
            ),
            reply_markup=destiny_guide_kb,
        )


@router.callback_query(F.data == 'destiny_guide')
@flags.with_client
async def destiny_guide(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        astro_events.get(date.today().strftime('%m.%Y')),
        reply_markup=to_destiny_guide_kb,
    )

    if not client.subscription_is_active():
        await query.message.answer(
            client.genderize(
                '<b>Ты {gender:увидел,увидела} только первую звезду.</b>\n'
                'Но на небе их гораздо больше.\n'
                '<b>Астрособытия месяца</b> — лишь часть картины.\n'
                '<b>Важные дни в твоих сферах</b>, энергетические пики, '
                'моменты ясности — всё это ждёт в <i>Путеводителе судьбы</i>.\n'
                '<b>Подписка откроет оба уровня доступа:</b>\n'
                '— к полной карте неба\n'
                '— и к важным поворотам именно в твоей жизни\n'
                'Пора видеть глубже.',
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Оформить подписку',
            ),
        )

    current_date = now()
    first_week_day = now() - timedelta(days=current_date.weekday())
    last_week_day = now() + timedelta(days=6)
    await ClientAction.objects.aget_or_create(
        client=client,
        action=Actions.DESTINY_GUIDE,
        date__gte=first_week_day,
        date__lte=last_week_day,
    )


@router.callback_query(F.data == 'important_days')
@flags.with_client
async def important_days_handler(query: CallbackQuery, client: Client):
    if not client.subscription_is_active():
        await query.message.edit_text(
            'Ты чувствуешь движение — но пока не видишь маршрута.\n'
            '<i>Важные дни</i> — это подсветка моментов,'
            'когда лучше действовать, ждать, говорить, молчать, начинать, завершать.\n'
            '✨ Это карта энергий месяца —'
            'персональная и точная.\n'
            '<b>Откроется с подпиской.</b>',
            parse_mode=ParseMode.HTML,
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Хочу видеть знаки',
            ),
        )
        return

    await query.message.edit_text(
        important_days.get(date.today().strftime('%m.%Y')),
        reply_markup=to_destiny_guide_kb,
    )
