from datetime import datetime

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message


async def validate_time(msg: Message):
    try:
        datetime.strptime(msg.text, '%H:%M')
    except ValueError:
        await msg.answer('Некорректное время. Попробуй еще раз')
        raise SkipHandler
