from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from core import tasks

router = Router()


@router.message(Command('test'))
async def test(msg: Message, command: CommandObject):
    func = getattr(tasks, command.args, None)
    if not func:
        await msg.answer('Нет такой функции')
        return

    func.delay()
