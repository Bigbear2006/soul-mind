import random
from datetime import date

from aiogram import F, Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.utils.timezone import now

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.premium_space import premium_space_kb
from bot.keyboards.utils import one_button_keyboard
from bot.numerology import get_life_path_number, get_power_day
from bot.templates.premium_space import (
    power_days_descriptions,
    universe_answers,
    universe_vip_advices,
)
from core.models import Actions, Client, ClientAction, SubscriptionPlans

router = Router()


@router.message(F.text == '💫 Премиум-пространство')
@router.callback_query(F.data == 'premium_space')
@flags.with_client
async def premium_space(
    msg: Message | CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await state.set_state(None)
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )

    if not client.is_registered():
        await answer_func(
            '💎 Премиум-пространство\n\n'
            'Это пространство для тех,\n'
            'кто готов услышать не только ответы,\n'
            'но и себя.',
            reply_markup=get_to_registration_kb(
                text='🔒 Зарегистрируйся и загляни в Премиум-пространство',
            ),
        )
    elif not client.has_trial() and not client.subscription_is_active():
        await answer_func(
            client.genderize(
                '💎 Премиум-пространство\n\n'
                'Ты уже {gender:почувствовал,почувствовала}, как Soul Muse ведёт.\n'
                'Но в этом пространстве она говорит иначе. Точнее. Глубже.\n'
                'Не для всех. Но для тебя — возможно.',
            ),
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Оформить доступ к Премиум-пространству',
            ),
        )
    elif client.subscription_plan == SubscriptionPlans.STANDARD:
        await answer_func(
            '💎 Премиум-пространство\n\n'
            'Ты уже слышишь Soul Muse — каждый день.\n'
            'Но есть место, где она говорит не словами, а ключами.\n'
            'Это Премиум-пространство. И оно ждёт.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Перейти на Премиум',
                only_premium=True,
            ),
        )
    elif client.subscription_plan == SubscriptionPlans.PREMIUM:
        await answer_func(
            client.genderize(
                '💎 Премиум-пространство\n\n'
                'Ты {gender:сделал,сделала} шаг глубже.\n'
                'А значит, теперь доступно не просто больше — доступно иное.\n\n'
                'Здесь я говорю только тебе.\n'
                'В нужное время. О самом важном.\n\n'
                'Добро пожаловать в Премиум-пространство.\n'
                'Открой — и почувствуй, как звучит твой следующий уровень.',
            ),
            reply_markup=premium_space_kb,
        )
    elif client.has_trial():
        await answer_func(
            client.genderize(
                '💎 Премиум-пространство\n\n'
                'Ты слушаешь Muse — и это уже много.\n'
                'Но Премиум-пространство — это не просто голос.\n'
                'Это глубина. Настоящие повороты. И ты к ним почти {gender:подошёл,подошла}.',
            ),
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Оформи подписку, чтобы войти в Премиум-пространство',
            ),
        )


@router.callback_query(F.data == 'power_day')
@flags.with_client
async def power_day_handler(query: CallbackQuery, client: Client):
    if not client.subscription_plan == SubscriptionPlans.PREMIUM:
        await query.message.edit_text(
            '🚀 Твой День силы\n\n'
            'Этот ключ доступен только для Премиум-подписчиков.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Перейти на Премиум',
            ),
        )
        return

    if await client.get_month_usages(Actions.POWER_DAY) >= 1:
        await query.message.edit_text(
            '🚀 Твой День силы\n\n'
            'Твой День силы ещё не наступил — я сообщу тебе, когда придёт время.',
        )
        return

    await query.message.edit_text(
        '🚀 Твой День силы\n\n'
        'Ты уже знаешь, когда твоя энергия разворачивается мощнее всего?\n'
        'Я вычислила эту дату по твоим кодам.\n'
        'У тебя будет один такой день в месяце.\n'
        'Выбери, как прожить его — с фокусом, с намерением, с собой.',
        reply_markup=one_button_keyboard(
            text='📅 Узнать свой День силы',
            callback_data='show_power_day',
            back_button_data='premium_space',
        ),
    )


@router.callback_query(F.data == 'show_power_day')
@flags.with_client
async def show_power_day(query: CallbackQuery, client: Client):
    power_day = get_power_day(client.birth.date())
    await query.message.edit_text(
        client.genderize(power_days_descriptions[power_day]),
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='power_day',
        ),
    )


@router.callback_query(F.data == 'universe_answer')
@flags.with_client
async def universe_answer_handler(query: CallbackQuery, client: Client):
    if not client.subscription_plan == SubscriptionPlans.PREMIUM:
        await query.message.edit_text(
            '✨ Ответ Вселенной\n\nДоступ только для Премиум-подписчиков.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Получить доступ к ответу Вселенной',
            ),
        )
        return

    if await client.get_month_usages(Actions.UNIVERSE_ANSWER) >= 1:
        await query.message.edit_text(
            client.genderize(
                '✨ Ответ Вселенной\n\n'
                'Ты уже {gender:получил,получила} ответ на этот месяц. '
                'Новый будет 1 числа.',
            ),
        )
        return

    await query.message.edit_text(
        client.genderize(
            '✨ Ответ Вселенной\n\n'
            'Один раз в месяц Вселенная говорит чётко.\n'
            'Я слушаю за тебя. И передаю.\n'
            'Этот ответ — не совет.\n'
            'Это то, что стоит услышать, даже если ты не {gender:спрашивал,спрашивала}.',
        ),
        reply_markup=one_button_keyboard(
            text='🪐 Получить ответ от Вселенной',
            callback_data='show_universe_answer',
            back_button_data='premium_space',
        ),
    )


@router.callback_query(F.data == 'show_universe_answer')
@flags.with_client
async def show_universe_answer(query: CallbackQuery, client: Client):
    lpn = get_life_path_number(client.birth.date())
    month_answers = universe_answers.get(
        date.today().strftime('%m.%Y'),
        {},
    )
    await query.message.edit_text(
        client.genderize(month_answers[lpn]),
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='universe_answer',
        ),
    )


@router.callback_query(F.data == 'soul_muse_vip_answer')
@flags.with_client
async def soul_muse_vip_answer(query: CallbackQuery, client: Client):
    if not client.subscription_plan == SubscriptionPlans.PREMIUM:
        await query.message.edit_text(
            '🔮 VIP-совет от Soul Muse\n\n'
            'Этот знак доступен только на Премиуме.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Оформить Премиум и получить совет',
            ),
        )
        return

    if await client.get_month_usages(Actions.SOUL_MUSE_VIP_ANSWER) >= 1:
        await query.message.edit_text(
            client.genderize(
                '🔮 VIP-совет от Soul Muse\n\n'
                'Ты уже {gender:получил,получила} VIP-совет в этом месяце.\n'
                'Новый будет доступен в следующем.',
            ),
            reply_markup=one_button_keyboard(
                text='Назад',
                callback_data='premium_space',
            ),
        )
        return

    await query.message.edit_text(
        client.genderize(
            '🔮 VIP-совет от Soul Muse\n\n'
            'Это не про информацию.\n'
            'Это как будто кто-то вложил тебе в ладонь знак.\n'
            'И ты {gender:почувствовал,почувствовала} — он твой.\n\n'
            '{gender:Готов,Готова}? Я передам.',
        ),
        reply_markup=one_button_keyboard(
            text='🔓 Получить совет от Muse',
            callback_data='show_vip_advice',
            back_button_data='premium_space',
        ),
    )


@router.callback_query(F.data == 'show_vip_advice')
@flags.with_client
async def show_vip_advice(query: CallbackQuery, client: Client):
    advice = random.choice(list(universe_vip_advices.values()))
    await query.message.edit_text(client.genderize(advice))
    await ClientAction.objects.aget_or_create(
        client=client,
        action=Actions.SOUL_MUSE_VIP_ANSWER,
        date__date=now().date(),
    )
