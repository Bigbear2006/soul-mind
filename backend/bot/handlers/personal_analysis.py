from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message

from bot.api.astrology import western_horoscope
from bot.keyboards.inline import back_to_personal_analysis_kb
from bot.templates import (
    get_career_and_finance_intro,
    get_destiny_mystery_intro,
    get_destiny_mystery_text,
    get_full_profile_intro,
    get_love_code_intro,
    get_personal_analysis_intro,
    get_superpower_intro,
)
from bot.templates.career_and_finance import get_career_and_finance_text
from bot.templates.full_profile import get_full_profile_text
from bot.templates.love_code import get_love_code_text
from bot.templates.superpower import get_superpower_text
from core.models import Client

router = Router()


@router.message(F.text == '📌 Личностный разбор')
@router.callback_query(F.data == 'to_personal_analysis')
@flags.with_client
async def personal_analysis_handler(
    msg: Message | CallbackQuery,
    client: Client,
):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    text, reply_markup = get_personal_analysis_intro(client)
    await answer_func(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == 'destiny_mystery')
@flags.with_client
async def destiny_mystery(query: CallbackQuery, client: Client):
    text, reply_markup = get_destiny_mystery_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_destiny_mystery')
@flags.with_client
async def show_destiny_mystery(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        get_destiny_mystery_text(client),
        reply_markup=back_to_personal_analysis_kb,
    )


@router.callback_query(F.data == 'career_and_finance')
@flags.with_client
async def career_and_finance(query: CallbackQuery, client: Client):
    text, reply_markup = get_career_and_finance_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_career_and_finance')
@flags.with_client
async def show_career_and_finance(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        get_career_and_finance_text(client),
        reply_markup=back_to_personal_analysis_kb,
    )


@router.callback_query(F.data == 'love_code')
@flags.with_client
async def love_code(query: CallbackQuery, client: Client):
    text, reply_markup = get_love_code_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_love_code')
@flags.with_client
async def show_love_code(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        get_love_code_text(client),
        reply_markup=back_to_personal_analysis_kb,
    )


@router.callback_query(F.data == 'superpower')
@flags.with_client
async def superpower(query: CallbackQuery, client: Client):
    text, reply_markup = get_superpower_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_superpower')
@flags.with_client
async def show_superpower(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        get_superpower_text(client),
        reply_markup=back_to_personal_analysis_kb,
    )


@router.callback_query(F.data == 'full_profile')
@flags.with_client
async def full_profile(query: CallbackQuery, client: Client):
    text, reply_markup = get_full_profile_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_full_profile')
@flags.with_client
async def show_full_profile(query: CallbackQuery, client: Client):
    # TODO: добавить текст для тестового периода
    intro, content, conclusion = get_full_profile_text(client)
    await query.message.edit_text(intro, reply_markup=None)
    await query.message.answer(content)
    await query.message.answer(
        intro,
        reply_markup=back_to_personal_analysis_kb,
    )
