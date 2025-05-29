from aiogram import F, Router, flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.vip_services import (
    get_answer_consult_kb,
    get_consults_list_kb,
)
from core.models import MiniConsult, Client

router = Router()


@router.message(Command('consults'))
@router.callback_query(F.data == 'consults_list')
@flags.with_client
async def consults_list(msg: Message | CallbackQuery, state: FSMContext, client: Client):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    await state.update_data(page=1)
    await answer_func(
        'Текущие консультации',
        reply_markup=await get_consults_list_kb(client),
    )


@router.callback_query(F.data.startswith('mini_consult'))
async def mini_consult_detail(query: CallbackQuery):
    consult = (
        await MiniConsult.objects.select_related('client', 'expert_type')
        .prefetch_related('topics__topic')
        .aget(pk=query.data.split(':')[1])
    )
    await consult.send_to(
        chat_id=query.message.chat.id,
        reply_markup=get_answer_consult_kb(
            consult.pk,
            back_button_data='delete_this_message',
        ),
    )


@router.callback_query(F.data == 'delete_this_message')
async def delete_this_message(query: CallbackQuery):
    await query.message.delete()


@router.callback_query(F.data.in_(('consults_previous', 'consults_next')))
@flags.with_client
async def change_consults_list_page(query: CallbackQuery, state: FSMContext, client: Client):
    page = await state.get_value('page')
    if query.data == 'consults_previous':
        page -= 1
    else:
        page += 1
    await state.update_data(page=page)

    await query.message.edit_text(
        'Текущие консультации',
        reply_markup=await get_consults_list_kb(client, page=page),
    )
