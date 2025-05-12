import json

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from bot.api.soul_muse import SoulMuse
from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.soul_muse_question import (
    buy_questions_kb,
    get_soul_muse_question_kb,
)
from bot.keyboards.inline.vip_services import get_payment_choices_kb
from bot.keyboards.utils import one_button_keyboard
from bot.loader import logger
from bot.prompts.answer_question import get_answer_question_prompt
from bot.prompts.categorize_question import get_categorize_question_prompt
from bot.settings import settings
from bot.states import SoulMuseQuestionState
from bot.templates.soul_muse_question import inappropriate_questions_answers
from core.models import (
    Actions,
    Client,
    ClientAction,
    ClientActionBuying,
    SoulMuseQuestion,
    SubscriptionPlans,
)

router = Router()


@router.message(F.text == '👩🏽 Спроси у Soul Muse')
@flags.with_client
async def soul_muse_question(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
            '👩🏽 Спроси у Soul Muse\n'
            'У тебя есть вопрос.\n'
            'Но я не могу услышать, пока ты не представился(ась).\n\n'
            'Пройди регистрацию — и тогда я отвечу. Не из ума. Из глубины.',
            reply_markup=get_to_registration_kb(
                text='🔓 Разблокировать доступ к вопросу',
            ),
        )
        return

    if await client.get_remaining_usages(Actions.SOUL_MUSE_QUESTION) > 0:
        remaining_usages = await client.get_remaining_usages(
            Actions.SOUL_MUSE_QUESTION,
        )
        remaining_usages_str = f'* У тебя осталось {remaining_usages} вопросов'
        if client.subscription_plan == SubscriptionPlans.PREMIUM:
            await msg.answer(
                '👩🏽 Спроси у Soul Muse\n'
                'У тебя есть пространство для настоящих вопросов.\n'
                'Пятнадцать шагов к себе — через ответы.\n\n'
                'Когда почувствуешь — просто задай. А я скажу, что ты давно знал(а), '
                'но боялся(ась) услышать.\n\n'
                f'{remaining_usages_str}',
                reply_markup=get_soul_muse_question_kb(
                    buy_extra_questions_btn=False,
                ),
            )
        elif client.subscription_plan == SubscriptionPlans.STANDARD:
            await msg.answer(
                '👩🏽 Спроси у Soul Muse\n'
                'Иногда один вопрос — открывает целый пласт.\n'
                'Ты можешь задать до 4 вопросов. А потом — расширить доступ.\n\n'
                'Готов(а)? Я отвечаю из тишины. Но попадаю в самое точное.\n\n'
                f'{remaining_usages_str}',
                reply_markup=get_soul_muse_question_kb(
                    buy_extra_questions_btn=False,
                ),
            )
        else:
            await msg.answer(
                '👩🏽 Спроси у Soul Muse\n'
                'Ты носишь в себе вопрос?\n'
                'О себе. О чувствах. О пути.\n'
                'Задай — и я отвечу. Точно, глубоко, без шаблонов.\n\n'
                'У тебя есть 2 вопроса. Используй их осознанно.\n\n'
                f'{remaining_usages_str}',
                reply_markup=get_soul_muse_question_kb(
                    buy_extra_questions_btn=False,
                ),
            )
        return

    if await client.get_remaining_usages(Actions.SOUL_MUSE_QUESTION) <= 0:
        if client.subscription_is_active():
            await msg.answer(
                '👩🏽 Спроси у Soul Muse\n'
                'Ты уже использовал(а) все включённые вопросы.\n\n'
                'Хочешь продолжить исследовать себя?\n\n'
                'Можешь докупить доступ и задать ещё.\n'
                'Я рядом.',
                reply_markup=get_soul_muse_question_kb(ask_question_btn=False),
            )
        else:
            await msg.answer(
                '👩🏽 Спроси у Soul Muse\n'
                'Ты уже почувствовал(а), как звучит мой голос.\n'
                'Но сейчас я молчу — пока ты не вернёшься.\n\n'
                'Оформи доступ — и я снова услышу твой вопрос.',
                reply_markup=get_to_subscription_plans_kb(),
            )


###########################
### BUY EXTRA QUESTIONS ###
###########################


@router.callback_query(F.data == 'buy_more_questions')
async def buy_more_questions(query: CallbackQuery):
    return await query.message.edit_text(
        'Сколько вопросов ты хочешь купить?\n\n'
        '1 персональный вопрос → 129 ₽ или 200 астробаллов\n'
        '5 персональных вопросов → 599 ₽ или 900 астробаллов',
        reply_markup=buy_questions_kb,
    )


@router.callback_query(F.data.startswith('buy_question'))
async def buy_question(query: CallbackQuery, state: FSMContext):
    buy_count = query.data.split(':')[1]
    await state.update_data(buy_count=buy_count)
    await state.set_state(SoulMuseQuestionState.payment_type)
    await query.message.edit_text(
        'Выбери тип оплаты',
        reply_markup=get_payment_choices_kb(
            '200 баллов' if buy_count == 'one' else '900 баллов',
            '129 ₽' if buy_count == 'one' else '599 ₽',
            back_button_data='buy_more_questions',
        ),
    )


@router.callback_query(
    F.data.in_(('astropoints', 'money')),
    StateFilter(SoulMuseQuestionState.payment_type),
)
@flags.with_client
async def choose_extra_questions_payment_type(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    buy_count = await state.get_value('buy_count')
    buy_count_str = '1' if buy_count == 'one' else '5'
    astropoints = 200 if buy_count == 'one' else 900
    money = 129 if buy_count == 'one' else 599

    if query.data == 'astropoints':
        if client.astropoints < astropoints:
            await query.message.answer('Не хватает астробаллов')
            return

        await ClientActionBuying.objects.acreate(
            client=client,
            action=Actions.SOUL_MUSE_QUESTION,
            count=1 if await state.get_value('buy_count') == 'one' else 5,
        )
        client.astropoints -= astropoints
        await client.asave()

        remaining_usages = await client.get_remaining_usages(
            Actions.SOUL_MUSE_QUESTION,
        )
        await query.message.edit_text(
            f'Теперь у тебя {remaining_usages} вопросов!',
        )
        await state.clear()
    else:
        await query.message.answer_invoice(
            f'Дополнительные вопросы ({buy_count_str})',
            f'Дополнительные вопросы ({buy_count_str})',
            'extra_questions',
            settings.CURRENCY,
            [LabeledPrice(label=settings.CURRENCY, amount=money * 100)],
            settings.PROVIDER_TOKEN,
        )
        await state.set_state(SoulMuseQuestionState.payment)


@router.pre_checkout_query(StateFilter(SoulMuseQuestionState.payment))
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@router.message(
    F.successful_payment,
    StateFilter(SoulMuseQuestionState.payment),
)
@flags.with_client
async def on_extra_questions_buying(
    msg: Message,
    state: FSMContext,
    client: Client,
):
    await ClientActionBuying.objects.acreate(
        client=client,
        action=Actions.SOUL_MUSE_QUESTION,
        count=1 if await state.get_value('buy_count') == 'one' else 5,
    )
    remaining_usages = await client.get_remaining_usages(
        Actions.SOUL_MUSE_QUESTION,
    )
    await msg.answer(f'Теперь у тебя {remaining_usages} вопросов!')
    await state.clear()


####################
### ASK QUESTION ###
####################


@router.callback_query(F.data == 'ask_soul_muse')
async def ask_soul_muse(query: CallbackQuery, state: FSMContext):
    await state.set_state(SoulMuseQuestionState.question)
    await query.message.edit_text(
        'Задай вопрос — и я отвечу.\n'
        'Максимальная длина вопроса - 250 символов.',
    )


@router.message(F.text, StateFilter(SoulMuseQuestionState.question))
@flags.with_client
async def soul_muse_answer(msg: Message, client: Client):
    if len(msg.text) > 250:
        await msg.answer(
            'Максимальная длина вопроса - 250 символов. Текст будет обрезан.',
        )
    soul_muse_face_msg = await msg.answer_photo(settings.MEDIA.soul_muse)

    muse = SoulMuse()
    data = await muse.answer(
        get_categorize_question_prompt(msg.text[:250]),
    )
    logger.info(data)
    data = json.loads(data)
    category = data['category']
    reason = data['reason']

    await ClientAction.objects.acreate(
        client=client,
        action=Actions.SOUL_MUSE_QUESTION,
    )

    kb = one_button_keyboard(text='В меню', callback_data='to_menu')
    if category == 'deep_personal':
        answer = await muse.answer(
            get_answer_question_prompt(client, msg.text[:250]),
            max_output_tokens=270,
        )
        await msg.answer(answer, reply_markup=kb)
    else:
        answer = inappropriate_questions_answers[category]
        await msg.answer(answer, reply_markup=kb)

    await soul_muse_face_msg.delete()
    await SoulMuseQuestion.objects.acreate(
        category=category,
        reason=reason,
        question=msg.text[:250],
        answer=answer,
    )
