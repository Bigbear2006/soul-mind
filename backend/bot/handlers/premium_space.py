import random
from datetime import date

from aiogram import F, Router, flags
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from django.utils.timezone import now

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.premium_space import premium_space_kb
from bot.keyboards.utils import one_button_keyboard
from bot.services.numerology import get_life_path_number, get_power_day
from bot.text_templates.premium_space import (
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
        return

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


@router.callback_query(F.data == 'power_day')
@flags.with_client
async def power_day_handler(query: CallbackQuery, client: Client):
    if (
        not client.subscription_is_active()
        or client.subscription_plan == SubscriptionPlans.PREMIUM
    ):
        await query.message.edit_text(
            '<b>🚀 Твой День силы</b>\n\n'
            '<b>У каждого месяца — есть своя вершина.</b>\n'
            'Именно в этот день ты чувствуешь подъём, ясность, силу.\n'
            'Я уже знаю, когда это для тебя.\n'
            '<b>Ты тоже можешь узнать — в Премиум-пространстве.</b>',
            parse_mode=ParseMode.HTML,
            reply_markup=get_to_subscription_plans_kb(
                text='🚀 Увидеть свой День силы',
                only_premium=True,
                back_button_data='premium_space',
            ),
        )
        return

    if await client.get_month_usages(Actions.POWER_DAY) >= 1:
        await query.message.edit_text(
            '🚀 Твой День силы\n\n'
            'Твой День силы ещё не наступил — я сообщу тебе, когда придёт время.',
            reply_markup=one_button_keyboard(
                text='Назад',
                callback_data='premium_space',
            ),
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
    text = client.genderize(power_days_descriptions[power_day])

    await query.message.edit_text(text)
    await query.message.answer_audio(
        BufferedInputFile.from_file(
            f'assets/audio/power_days/{power_day}_{client.gender}.wav',
            'Твой День силы.wav',
        ),
    )

    await ClientAction.objects.aget_or_create(
        client=client,
        action=Actions.POWER_DAY,
        date__date=now().date(),
    )


@router.callback_query(F.data == 'universe_answer')
@flags.with_client
async def universe_answer_handler(query: CallbackQuery, client: Client):
    if (
        not client.subscription_is_active()
        or client.subscription_plan == SubscriptionPlans.PREMIUM
    ):
        await query.message.edit_text(
            client.genderize(
                '<b>✨ Ответ Вселенной</b>\n\n'
                '<b>Иногда ты просто задаёшь вопрос — и ждёшь знак.</b>\n'
                'В Премиум-пространстве он приходит.\n'
                '<b>Один раз в месяц — для важного.</b>\n'
                '{gender:Готов,Готова} услышать?',
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_to_subscription_plans_kb(
                text='🔮 Получить через Премиум',
                only_premium=True,
                back_button_data='premium_space',
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
            reply_markup=one_button_keyboard(
                text='Назад',
                callback_data='premium_space',
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
    if (
        not client.subscription_is_active()
        or client.subscription_plan == SubscriptionPlans.PREMIUM
    ):
        await query.message.edit_text(
            '<b>🔮 VIP-совет</b>\n\n'
            '<b>Когда не хочется объяснений — а хочется знак.</b>\n'
            'Это не прогноз, не аналитика. Это голос,\n'
            'который будто знал, что ты сейчас в этом.\n'
            '<b>Один раз в месяц. Только в Премиум.</b>',
            parse_mode=ParseMode.HTML,
            reply_markup=get_to_subscription_plans_kb(
                text='✨ Получить через Премиум',
                only_premium=True,
                back_button_data='premium_space',
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
    advice_key = random.choice(list(universe_vip_advices.keys()))
    advice_value = client.genderize(universe_vip_advices[advice_key])

    await query.message.edit_text(f'{advice_key}\n\n{advice_value}')
    await query.message.answer_audio(
        BufferedInputFile.from_file(
            f'assets/audio/universe_vip_advices/{advice_key}_{client.gender}.wav',
            'VIP-совет от Soul Muse.wav',
        ),
    )

    await ClientAction.objects.aget_or_create(
        client=client,
        action=Actions.SOUL_MUSE_VIP_ANSWER,
        date__date=now().date(),
    )
