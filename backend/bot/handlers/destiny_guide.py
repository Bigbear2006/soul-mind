from datetime import date, timedelta

from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message
from django.utils.timezone import now

from bot.keyboards.inline.base import get_to_registration_kb
from bot.keyboards.utils import one_button_keyboard
from bot.templates.destiny_guide import astro_events, important_days
from core.choices import Actions
from core.models import Client, ClientAction

router = Router()


@router.message(F.text == '🗺️ Путеводитель судьбы')
@flags.with_client
async def destiny_guide_intro(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
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
        await msg.answer(
            '🗺️ Путеводитель судьбы\n\n'
            'Я держу руку на пульсе космоса —\n'
            'и каждый месяц собираю для тебя карту:\n'
            'когда начинать, когда наблюдать, когда беречь, а когда сиять.\n\n'
            'Астрособытия. Важные дни. Личное направление.',
            reply_markup=one_button_keyboard(
                text='🌠 Смотреть Путеводитель',
                callback_data='destiny_guide',
            ),
        )
    elif client.has_trial():
        await msg.answer(
            '🗺️ Путеводитель судьбы\n\n'
            'Ретрограды, затмения, важные транзиты —\n'
            'я собрала всё, что двигает пространство.\n'
            'Ты видишь главное. Остальное раскроется, если захочешь глубже.\n\n'
            'Хочешь знать, с какой энергией входит месяц?',
            reply_markup=one_button_keyboard(
                text='🌌 Открыть астрособытия',
                callback_data='destiny_guide',
            ),
        )
    else:
        await msg.answer(
            client.genderize(
                '🗺️ Путеводитель судьбы\n\n'
                'Ты видишь главное —\n'
                'ретрограды, затмения, ключевые движения неба.\n'
                'Этого уже достаточно, чтобы идти осознанно.\n'
                'Но я могу показать больше… когда ты будешь {gender:готов,готова}.\n\n'
                'P.S. Подписка откроет доступ к важным дням в твоих сферах.',
            ),
            reply_markup=one_button_keyboard(
                text='🌘 Смотреть астрособытия месяца',
                callback_data='destiny_guide',
            ),
        )


@router.callback_query(F.data == 'destiny_guide')
@flags.with_client
async def destiny_guide(query: CallbackQuery, client: Client):
    reply_markup = None
    if client.subscription_is_active():
        reply_markup = one_button_keyboard(
            text='🌘 Смотреть важные дни месяца',
            callback_data='important_days',
        )
    await query.message.edit_text(
        astro_events.get(date.today().strftime('%m.%Y')),
        reply_markup=reply_markup,
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
async def important_days_handler(query: CallbackQuery):
    await query.message.edit_text(
        important_days.get(date.today().strftime('%m.%Y')),
        reply_markup=one_button_keyboard(
            text='🌘 Смотреть астрособытия месяца',
            callback_data='destiny_guide',
        ),
    )
