from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.inline import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from core.models import Client

router = Router()


@router.message(F.text == '🎁 Пятничный подарок')
async def friday_gift(msg: Message):
    client: Client = await Client.objects.aget(pk=msg.chat.id)

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
