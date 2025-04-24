import json

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.api.soul_muse import SoulMuse
from bot.keyboards.inline import (
    get_soul_muse_question_kb,
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.loader import logger
from bot.states import SoulMuseQuestionState
from bot.templates.soul_muse_question import inappropriate_questions_answers
from core.models import Actions, Client, SubscriptionPlans

# TODO: лимит на количеств запросов
# TODO: сохранение запросов с категориями в бд

router = Router()


@router.message(F.text == '🤖 Спроси у Soul Muse')
@flags.with_client
async def soul_muse_question(msg: Message, state: FSMContext, client: Client):
    if not client.is_registered():
        await msg.answer(
            '🤖 Спроси у Soul Muse\n'
            'У тебя есть вопрос.\n'
            'Но я не могу услышать, пока ты не представился(ась).\n\n'
            'Пройди регистрацию — и тогда я отвечу. Не из ума. Из глубины.',
            reply_markup=get_to_registration_kb(
                text='🔓 Разблокировать доступ к вопросу',
            ),
        )
        return

    if client.has_action_permission(Actions.SOUL_MUSE_QUESTION):
        await state.set_state(SoulMuseQuestionState.question)
        if client.subscription_plan == SubscriptionPlans.PREMIUM:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'У тебя есть пространство для настоящих вопросов.\n'
                'Пятнадцать шагов к себе — через ответы.\n\n'
                'Когда почувствуешь — просто задай. А я скажу, что ты давно знал(а), но боялся(ась) услышать.',
                reply_markup=get_soul_muse_question_kb(
                    buy_extra_questions_btn=False,
                ),
            )
        elif client.subscription_plan == SubscriptionPlans.STANDARD:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Иногда один вопрос — открывает целый пласт.\n'
                'Ты можешь задать до 4 вопросов. А потом — расширить доступ.\n\n'
                'Готов(а)? Я отвечаю из тишины. Но попадаю в самое точное.',
                reply_markup=get_soul_muse_question_kb(
                    buy_extra_questions_btn=False,
                ),
            )
        else:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Ты носишь в себе вопрос?\n'
                'О себе. О чувствах. О пути.\n'
                'Задай — и я отвечу. Точно, глубоко, без шаблонов.\n\n'
                'У тебя есть 2 вопроса. Используй их осознанно.',
                reply_markup=get_soul_muse_question_kb(
                    buy_extra_questions_btn=False,
                ),
            )
        return

    if client.action_limit_exceed(Actions.SOUL_MUSE_QUESTION):
        if client.subscription_is_active():
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Ты уже использовал(а) все включённые вопросы.\n\n'
                'Хочешь продолжить исследовать себя?\n\n'
                'Можешь докупить доступ и задать ещё.\n'
                'Я рядом.',
                reply_markup=get_soul_muse_question_kb(ask_question_btn=False),
            )
        else:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Ты уже почувствовал(а), как звучит мой голос.\n'
                'Но сейчас я молчу — пока ты не вернёшься.\n\n'
                'Оформи доступ — и я снова услышу твой вопрос.',
                reply_markup=get_to_subscription_plans_kb(),
            )


@router.callback_query(F.data == 'ask_soul_muse')
async def ask_soul_muse(query: CallbackQuery):
    await query.message.edit_text(
        'Задай вопрос — и я отвечу.\n'
        'Максимальная длина вопроса - 250 символов.',
    )


@router.message(F.text, StateFilter(SoulMuseQuestionState.question))
async def ask_soul_muse(msg: Message, state: FSMContext):
    if len(msg.text) > 250:
        await msg.answer(
            'Максимальная длина вопроса - 250 символов. Текст будет обрезан.',
        )

    muse = SoulMuse()
    category = await muse.categorize_question(msg.text[:250])
    logger.info(category)
    category = json.loads(category)['category']

    if category == 'deep_personal':
        answer = await muse.answer(msg.text[:250])
        await msg.answer(answer)
    else:
        await msg.answer(inappropriate_questions_answers[category])
    await state.clear()
