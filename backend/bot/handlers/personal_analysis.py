from aiogram import F, Router, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.keyboards.inline.base import get_to_subscription_plans_kb
from bot.keyboards.inline.personal_analysis import back_to_personal_analysis_kb
from bot.pdf import generate_pdf
from bot.templates.career_and_finance import (
    get_career_and_finance_intro,
    get_career_and_finance_text,
)
from bot.templates.destiny_mystery import (
    get_destiny_mystery_intro,
    get_destiny_mystery_text,
)
from bot.templates.full_profile import (
    get_full_profile_intro,
    get_full_profile_text,
)
from bot.templates.love_code import get_love_code_intro, get_love_code_text
from bot.templates.personal_analysis import get_personal_analysis_intro
from bot.templates.superpower import get_superpower_intro, get_superpower_text
from bot.text_utils import split_text
from core.models import Client

router = Router()


async def send_long_message(msg: Message, state: FSMContext, text: str):
    if len(text) > 4000:
        text_parts = split_text(text, max_length=4000, sep='\n')
        print(len(text_parts))
        msg_to_delete = await msg.edit_text(text_parts[0])
        await state.update_data(msg_to_delete_id=msg_to_delete.message_id)
        await msg.answer(
            text_parts[1],
            reply_markup=back_to_personal_analysis_kb,
        )
    else:
        await msg.edit_text(
            text,
            reply_markup=back_to_personal_analysis_kb,
        )


@router.message(F.text == '📌 Личностный разбор')
@router.callback_query(F.data == 'to_personal_analysis')
@flags.with_client
async def personal_analysis_handler(
    msg: Message | CallbackQuery,
    state: FSMContext,
    client: Client,
):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    if msg_to_delete_id := await state.get_value('msg_to_delete_id'):
        try:
            await msg.bot.delete_message(client.pk, msg_to_delete_id)
            await state.update_data(msg_to_delete_id=None)
        except TelegramBadRequest:
            pass
    text, reply_markup = get_personal_analysis_intro(client)
    await answer_func(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == 'destiny_mystery')
@flags.with_client
async def destiny_mystery(query: CallbackQuery, client: Client):
    text, reply_markup = get_destiny_mystery_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_destiny_mystery')
@flags.with_client
async def show_destiny_mystery(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await send_long_message(
        query.message,
        state,
        get_destiny_mystery_text(client),
    )


@router.callback_query(F.data == 'career_and_finance')
@flags.with_client
async def career_and_finance(query: CallbackQuery, client: Client):
    text, reply_markup = get_career_and_finance_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_career_and_finance')
@flags.with_client
async def show_career_and_finance(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await send_long_message(
        query.message,
        state,
        get_career_and_finance_text(client),
    )


@router.callback_query(F.data == 'love_code')
@flags.with_client
async def love_code(query: CallbackQuery, client: Client):
    text, reply_markup = get_love_code_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_love_code')
@flags.with_client
async def show_love_code(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await send_long_message(query.message, state, get_love_code_text(client))


@router.callback_query(F.data == 'superpower')
@flags.with_client
async def superpower(query: CallbackQuery, client: Client):
    text, reply_markup = get_superpower_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_superpower')
@flags.with_client
async def show_superpower(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await send_long_message(query.message, state, get_superpower_text(client))


@router.callback_query(F.data == 'full_profile')
@flags.with_client
async def full_profile(query: CallbackQuery, client: Client):
    text, reply_markup = get_full_profile_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_full_profile')
@flags.with_client
async def show_full_profile(query: CallbackQuery, client: Client):
    intro, content, conclusion = get_full_profile_text(client)
    if client.subscription_is_active():
        text = '\n\n'.join([intro, *content, conclusion])
        await query.message.answer_document(
            BufferedInputFile(generate_pdf(text), 'Твой полный профиль.pdf'),
        )
    elif client.has_trial():
        text = '\n\n'.join([intro, *content])
        await query.message.answer_document(
            BufferedInputFile(generate_pdf(text), 'Твой полный профиль.pdf'),
            caption=conclusion,
            reply_markup=get_to_subscription_plans_kb(
                text='Оформить подписку',
            ),
        )
