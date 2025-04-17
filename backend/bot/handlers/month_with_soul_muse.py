from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
    month_with_soul_muse_kb,
)
from bot.keyboards.utils import one_button_keyboard
from core.models import Client, SubscriptionPlans

router = Router()


@router.message(F.text == '📄 Месяц с Soul Muse')
@router.callback_query(F.data == 'month_with_soul_muse')
async def month_with_soul_muse(msg: Message | CallbackQuery):
    pk = msg.chat.id if isinstance(msg, Message) else msg.message.chat.id
    client: Client = await Client.objects.aget(pk=pk)
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )

    if not client.is_registered():
        await answer_func(
            '📄 Месяц с Soul Muse\n\n'
            'Я читаю месяц как карту:\n'
            'где ускориться, где остановиться, где просто быть.\n'
            'Но чтобы открыть тебе это — мне нужно знать, кто ты.\n\n'
            'Зарегистрируйся, и я покажу, с чем ты входишь в этот месяц.',
            reply_markup=get_to_registration_kb(
                text='🔒 Зарегистрироваться и разблокировать прогноз',
            ),
        )
    elif client.subscription_is_active():
        await answer_func(
            '📄 Месяц с Soul Muse\n\n'
            'Каждый месяц несёт свою энергию.\n'
            'Я уже почувствовала, куда он ведёт тебя.\n\n'
            'Хочешь знать, в чём твой фокус, ресурс и сюжет?\n'
            'Открой — и двигайся не наугад, а в резонансе.',
            reply_markup=month_with_soul_muse_kb,
        )
    elif client.has_trial():
        await answer_func(
            '📄 Месяц с Soul Muse\n\n'
            'Ты уже начал(а) путь.\n'
            'Но для прогноза на месяц, главного ресурса и личного сценария —\n'
            'нужно чуть больше доверия. И чуть глубже вход.\n\n'
            'Подписка откроет для тебя карту месяца — без догадок, с направлением.',
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Оформить подписку и заглянуть в свой месяц',
            ),
        )
    else:
        await answer_func(
            '📄 Месяц с Soul Muse\n\n'
            'Есть знание, которое приходит не сразу.\n'
            'Оно раскрывается, когда ты готов(а) видеть больше, чем просто день.\n'
            'Внутри — твой месяц. С фокусом. С ресурсом. С сюжетом.\n\n'
            'Оформи подписку — и я покажу всё.',
            reply_markup=get_to_subscription_plans_kb(
                text='🔓 Получить доступ к своему месяцу с Soul Muse',
            ),
        )


@router.callback_query(F.data == 'month_forecast')
async def month_forecast(query: CallbackQuery):
    await query.message.edit_text(
        '🎁 Персональный прогноз на месяц\n\n'
        'Хочешь знать, с чем ты входишь в этот месяц?\n'
        'Я собрала для тебя главное: настроение, фокус, потоки.\n'
        'Чтобы ты чувствовал(а) не хаос — а направление.',
        reply_markup=one_button_keyboard(
            text='📄 Открыть прогноз',
            callback_data='month_forecast_open',
            back_button_data='month_with_soul_muse',
        ),
    )


@router.callback_query(F.data == 'month_main_resource')
async def month_main_resource(query: CallbackQuery):
    await query.message.edit_text(
        '🎁 Главный ресурс месяца\n\n'
        'Каждый месяц дарит тебе что-то особенное.\n'
        'Этот ресурс — уже внутри.\n'
        'Я помогу его распознать и опереться на него.',
        reply_markup=one_button_keyboard(
            text='🪶 Узнать свой ресурс',
            callback_data='month_resource_open',
            back_button_data='month_with_soul_muse',
        ),
    )


@router.callback_query(F.data == 'month_script')
async def month_script(query: CallbackQuery):
    client: Client = await Client.objects.aget(pk=query.message.chat.id)

    if (
        client.subscription_is_active()
        and client.subscription_plan == SubscriptionPlans.PREMIUM
    ):
        await query.message.edit_text(
            '🎁 Твой сценарий месяца\n\n'
            'Ты — не просто участник. Ты — главный герой.\n'
            'Я прочитала твою карту и написала тебе сценарий:\n'
            'что станет вызовом, где поворот, когда выход на свет.',
            reply_markup=one_button_keyboard(
                text='🎬 Открыть сценарий месяца',
                callback_data='month_script_open',
                back_button_data='month_with_soul_muse',
            ),
        )
    else:
        await query.message.edit_text(
            '🎁 Твой сценарий месяца [🔒 Доступен на Премиум]\n\n'
            'Каждый месяц — как глава.\n'
            'Но только Премиум-подписчики получают свой личный сценарий.\n\n'
            'Я уже знаю, где в этом месяце твой поворот.\n'
            'Хочешь — покажу.',
            reply_markup=get_to_subscription_plans_kb(
                text='💎 Оформить Премиум и открыть сценарий',
            ),
        )
