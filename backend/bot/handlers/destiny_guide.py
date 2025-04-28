from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.base import get_to_registration_kb
from bot.keyboards.utils import one_button_keyboard
from bot.templates.destiny_guide import astro_events, important_days
from core.models import Client

# TODO: подсвечивать внутри бота, что Путеводитель на этой неделе еще не открыт

router = Router()


@router.message(F.text == '🗺️ Путеводитель судьбы')
@flags.with_client
async def destiny_guide_intro(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
            '🗺️ Путеводитель судьбы\n\n'
            'Звёзды знают, где ты.\n'
            'Но пока ты не заявил(а) о себе — я не могу показать тебе их маршрут.\n\n'
            'Пройди регистрацию — и я дам тебе карту того, что приближается.',
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
            '🗺️ Путеводитель судьбы\n\n'
            'Ты видишь главное —\n'
            'ретрограды, затмения, ключевые движения неба.\n'
            'Этого уже достаточно, чтобы идти осознанно.\n'
            'Но я могу показать больше… когда ты будешь готов(а).\n\n'
            'P.S. Подписка откроет доступ к важным дням в твоих сферах.',
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
        # for prod: date.today().strftime('%m.%Y')
        astro_events.get('05.2025'),
        reply_markup=reply_markup,
    )


@router.callback_query(F.data == 'important_days')
async def important_days_handler(query: CallbackQuery):
    await query.message.edit_text(
        # for prod: date.today().strftime('%m.%Y')
        important_days.get('05.2025'),
        reply_markup=one_button_keyboard(
            text='🌘 Смотреть астрособытия месяца',
            callback_data='destiny_guide',
        ),
    )
