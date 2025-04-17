from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message

from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from core.models import Client

router = Router()


@router.message(F.text == '🤝 Пригласить друга')
async def invite_friend(msg: Message):
    await msg.answer(
        'Если тебе здесь стало легче, глубже, тише —\n'
        'передай это тому, кто тоже ищет.\n'
        'Астробаллы — просто бонус.\n'
        'Главное — ты открываешь кому-то дверь.',
        reply_markup=one_button_keyboard(
            text='🌟 Поделиться SoulMind',
            callback_data='invite_friend',
        ),
    )


@router.callback_query(F.data == 'invite_friend')
@flags.with_client
async def invite_friend_2(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        'Отправь другу свою персональную ссылку:\n'
        f'{settings.BOT_LINK}?start={client.pk}\n'
        'Если друг оформит платную подписку, ты получишь +150 астробаллов. '
        'Накопленные баллы можно тратить на мини-консультации, '
        'дополнительную совместимость или персональные отчёты!',
    )
