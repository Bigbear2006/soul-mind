from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
    premium_space_kb,
)
from bot.keyboards.utils import one_button_keyboard
from core.models import Actions, Client, SubscriptionPlans

router = Router()


@router.message(F.text == '💫 Премиум-пространство')
@router.callback_query(F.data == 'premium_space')
async def premium_space(msg: Message | CallbackQuery):
    pk = msg.chat.id if isinstance(msg, Message) else msg.message.chat.id
    client: Client = await Client.objects.aget(pk=pk)
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
    elif not client.has_trial() or not client.subscription_is_active():
        await answer_func(
            '💎 Премиум-пространство\n\n'
            'Ты уже почувствовал(а), как Soul Muse ведёт.\n'
            'Но в этом пространстве она говорит иначе. Точнее. Глубже.\n'
            'Не для всех. Но для тебя — возможно.',
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
            ),
        )
    elif client.subscription_plan == SubscriptionPlans.PREMIUM:
        await answer_func(
            '💎 Премиум-пространство\n\n'
            'Ты сделал(а) шаг глубже.\n'
            'А значит, теперь доступно не просто больше — доступно иное.\n\n'
            'Здесь я говорю только тебе.\n'
            'В нужное время. О самом важном.\n\n'
            'Добро пожаловать в Премиум-пространство.\n'
            'Открой — и почувствуй, как звучит твой следующий уровень.',
            reply_markup=premium_space_kb
        )
    elif client.has_trial():
        await answer_func(
            '💎 Премиум-пространство\n\n'
            'Ты слушаешь Muse — и это уже много.\n'
            'Но Премиум-пространство — это не просто голос.\n'
            'Это глубина. Настоящие повороты. И ты к ним почти подошёл(шла).',
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Оформи подписку, чтобы войти в Премиум-пространство',
            ),
        )


@router.callback_query(F.data == 'power_day')
async def power_day(query: CallbackQuery):
    client: Client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.subscription_plan == SubscriptionPlans.PREMIUM:
        await query.message.edit_text(
            '🚀 Твой День силы\n\n'
            'Этот ключ доступен только для Премиум-подписчиков.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Перейти на Премиум',
            ),
        )
        return

    if not client.has_action_permission(Actions.POWER_DAY):
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


@router.callback_query(F.data == 'universe_answer')
async def universe_answer(query: CallbackQuery):
    client: Client = await Client.objects.aget(pk=query.from_user.id)

    if not client.subscription_plan == SubscriptionPlans.PREMIUM:
        await query.message.edit_text(
            '✨ Ответ Вселенной\n\nДоступ только для Премиум-подписчиков.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Получить доступ к ответу Вселенной',
            ),
        )
        return

    if not client.has_action_permission(Actions.UNIVERSE_ANSWER):
        await query.message.edit_text(
            '✨ Ответ Вселенной\n\n'
            'Ты уже получил(а) ответ на этот месяц. Новый будет 1 числа.',
        )
        return

    await query.message.edit_text(
        '✨ Ответ Вселенной\n\n'
        'Один раз в месяц Вселенная говорит чётко.\n'
        'Я слушаю за тебя. И передаю.\n'
        'Этот ответ — не совет.\n'
        'Это то, что стоит услышать, даже если ты не спрашивал(а).',
        reply_markup=one_button_keyboard(
            text='🪐 Получить ответ от Вселенной',
            callback_data='show_universe_answer',
            back_button_data='premium_space',
        ),
    )


@router.callback_query(F.data == 'soul_muse_vip_answer')
async def soul_muse_vip_answer(query: CallbackQuery):
    client: Client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.subscription_plan == SubscriptionPlans.PREMIUM:
        await query.message.edit_text(
            '🔮 VIP-совет от Soul Muse\n\n'
            'Этот знак доступен только на Премиуме.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Оформить Премиум и получить совет',
            ),
        )
        return

    if not client.has_action_permission(Actions.SOUL_MUSE_VIP_ANSWER):
        await query.message.edit_text(
            '🔮 VIP-совет от Soul Muse\n\n'
            'Ты уже получил(а) VIP-совет в этом месяце.\n'
            'Новый будет доступен в следующем.',
        )
        return

    await query.message.edit_text(
        '🔮 VIP-совет от Soul Muse\n\n'
        'Это не про информацию.\n'
        'Это как будто кто-то вложил тебе в ладонь знак.\n'
        'И ты почувствовал(а) — он твой.\n\n'
        'Готов(а)? Я передам.',
        reply_markup=one_button_keyboard(
            text='🔓 Получить совет от Muse',
            callback_data='show_vip_advice',
            back_button_data='premium_space',
        ),
    )
