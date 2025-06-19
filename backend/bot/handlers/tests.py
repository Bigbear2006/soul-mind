from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from core import tasks

router = Router()


@router.message(Command('test'))
async def test(msg: Message, command: CommandObject):
    if not msg.chat.id in (1736885484,):
        return

    if func:= getattr(tasks, command.args, None):
        func.delay()
        await msg.answer('Success!')
