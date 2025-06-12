from aiogram import F, Router, flags
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.keyboards.inline.base import get_to_subscription_plans_kb
from bot.services.personal_analysis.career_and_finance import (
    get_career_and_finance_intro,
    get_career_and_finance_text,
)
from bot.services.personal_analysis.destiny_mystery import (
    get_destiny_mystery_intro,
    get_destiny_mystery_text,
)
from bot.services.personal_analysis.full_profile import (
    get_full_profile_intro,
    get_full_profile_text,
)
from bot.services.personal_analysis.intro import get_personal_analysis_intro
from bot.services.personal_analysis.love_code import (
    get_love_code_intro,
    get_love_code_text,
)
from bot.services.personal_analysis.superpower import (
    get_superpower_intro,
    get_superpower_text,
)
from bot.utils.pdf import generate_pdf
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
    await query.message.answer_document(
        BufferedInputFile(
            generate_pdf(get_destiny_mystery_text(client)),
            'Тайна твоего предназначения.pdf',
        ),
    )


@router.callback_query(F.data == 'career_and_finance')
@flags.with_client
async def career_and_finance(query: CallbackQuery, client: Client):
    text, reply_markup = get_career_and_finance_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_career_and_finance')
@flags.with_client
async def show_career_and_finance(query: CallbackQuery, client: Client):
    await query.message.answer_document(
        BufferedInputFile(
            generate_pdf(get_career_and_finance_text(client)),
            'Карьера и финансы.pdf',
        ),
    )


@router.callback_query(F.data == 'love_code')
@flags.with_client
async def love_code(query: CallbackQuery, client: Client):
    text, reply_markup = get_love_code_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_love_code')
@flags.with_client
async def show_love_code(query: CallbackQuery, client: Client):
    await query.message.answer_document(
        BufferedInputFile(
            generate_pdf(get_love_code_text(client)),
            'Твой код любви.pdf',
        ),
    )


@router.callback_query(F.data == 'superpower')
@flags.with_client
async def superpower(query: CallbackQuery, client: Client):
    text, reply_markup = get_superpower_intro(client)
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data == 'show_superpower')
@flags.with_client
async def show_superpower(query: CallbackQuery, client: Client):
    await query.message.answer_document(
        BufferedInputFile(
            generate_pdf(get_superpower_text(client)),
            'Твоя суперсила.pdf',
        ),
    )


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
        )
        await query.message.answer(
            conclusion,
            reply_markup=get_to_subscription_plans_kb(
                text='Оформить подписку',
            ),
        )
