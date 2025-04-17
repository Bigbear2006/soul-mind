from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.keyboards.reply import menu_kb

router = Router()


@router.message(F.text == 'В меню')
async def to_menu_message_handler(msg: Message):
    await msg.answer('Главное меню', reply_markup=menu_kb)


@router.callback_query(F.data == 'to_menu')
async def to_menu_callback_query_handler(query: CallbackQuery):
    await query.message.answer('Главное меню', reply_markup=menu_kb)


@router.message(F.text == 'rm')
async def rm(msg: Message):
    await msg.answer('Клавиатура удалена', reply_markup=ReplyKeyboardRemove())
