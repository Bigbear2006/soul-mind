import random

from aiogram import F, Router, flags
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.templates.friday_gift import (
    friday_gifts_order,
    insight_phrases,
    symbols,
    friday_gifts_preambles,
)
from core.models import Client, ClientAction, Actions

# TODO: Добавить чередование и сохранение подарков

router = Router()


@router.message(F.text == '🎁 Пятничный подарок')
@flags.with_client
async def friday_gift_intro(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
            '🎁 Пятничный подарок от Soul Muse\n\n'
            'Здесь появляются подарки.\n'
            'Они не про скидки — они про душу.\n'
            'Каждую пятницу Soul Muse приносит знак, образ или фразу — '
            'для тех, кто уже на связи с собой.',
            reply_markup=get_to_registration_kb(
                text='🔒 Зарегистрируйся, чтобы получить свой первый подарок',
            ),
        )
    elif client.subscription_is_active():
        await msg.answer(
            '🎁 Пятничный подарок от Soul Muse\n\n'
            'Каждую пятницу Soul Muse вытягивает тебе знак.\n'
            'Иногда это карта. Иногда — образ. Иногда — фраза, которую ты давно ждал(а).\n'
            'Это не прогноз. Это приглашение прислушаться.\n\n'
            'Открой — если готов(а) услышать.',
            reply_markup=one_button_keyboard(
                text='🎁 Получить подарок недели',
                callback_data='friday_gift',
            ),
        )
    elif client.has_trial():
        await msg.answer(
            '🎁 Пятничный подарок от Soul Muse\n\n'
            'Твоё первое касание с Soul Muse — уже здесь.\n'
            'Я принесла тебе один случайный инсайт.\n'
            'Открой — и посмотри, откликнется ли.',
            reply_markup=one_button_keyboard(
                text='🎁 Получить подарок от Soul Muse',
                callback_data='friday_gift',
            ),
        )
    else:
        await msg.answer(
            '🎁 Пятничный подарок от Soul Muse\n\n'
            'Ты уже получил(а) подарок.\n'
            'Но Muse не даёт один раз.\n'
            'Каждую пятницу — новый знак. Новый смысл. Новая ты.',
            reply_markup=get_to_subscription_plans_kb(
                text='🔒 Оформи подписку и получай каждую неделю',
            ),
        )


@router.callback_query(F.data == 'friday_gift')
async def friday_gift(query: CallbackQuery):
    client_id = query.message.chat.id
    gift = random.choice(list(friday_gifts_order.keys()))
    preamble = friday_gifts_preambles[gift]

    if gift == 'insight_phrases':
        await query.message.edit_text(
            preamble + random.choice(insight_phrases),
        )
    elif gift == 'cards':
        card = random.choice(insight_phrases)
        await query.message.edit_text(f'{card["card"]}\n\n{card["text"]}')
    elif gift == 'symbols':
        await query.message.edit_text(preamble + random.choice(symbols))

    await ClientAction.objects.acreate(
        client_id=client_id, action=Actions.FRIDAY_GIFT
    )
