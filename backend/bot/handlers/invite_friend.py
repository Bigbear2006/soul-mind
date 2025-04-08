from aiogram import F, Router, flags
from aiogram.types import Message

from bot.settings import settings
from core.models import Client

router = Router()


@router.message(F.text == '🤝 Пригласить друга')
@flags.with_client
async def invite_friends_handler(msg: Message, client: Client):
    await msg.answer(
        'Отправь другу свою персональную ссылку:\n'
        f'{settings.BOT_LINK}?start={client.pk}\n'
        'Если друг оформит платную подписку, ты получишь +150 астробаллов. '
        'Накопленные баллы можно тратить на мини-консультации, '
        'дополнительную совместимость или персональные отчёты!',
    )
