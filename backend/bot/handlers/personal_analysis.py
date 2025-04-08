from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.inline import personal_analysis_kb

router = Router()


@router.message(F.text == '📌 Личностный разбор')
async def personal_analysis_handler(msg: Message):
    await msg.answer('Выберите тему', reply_markup=personal_analysis_kb)
