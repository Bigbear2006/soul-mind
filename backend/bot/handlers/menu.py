from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.reply import menu_kb

router = Router()


@router.message(Command('menu'))
async def to_menu_message_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Главное меню', reply_markup=menu_kb)


@router.callback_query(F.data == 'to_menu')
async def to_menu_callback_query_handler(
    query: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await query.message.answer('Главное меню', reply_markup=menu_kb)
