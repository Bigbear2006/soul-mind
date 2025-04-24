from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import get_to_registration_kb, get_weekly_quest_kb
from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from core.models import Client, ClientWeeklyQuest, WeeklyQuest

# TODO: Кастомизация и теги

router = Router()


@router.message(F.text == '🧩 Практики для роста')
@router.callback_query(F.data == 'to_weekly_quests_list')
@flags.with_client
async def weekly_quests_list(msg: Message | CallbackQuery, client: Client):
    if not client.is_registered():
        await msg.answer(
            '🧩 Практики для роста\n\n'
            'Хочешь расти — начни с первого шага.\n'
            'Но чтобы двигаться — надо появиться.\n\n'
            'Зарегистрируйся, и я открою тебе первый челлендж.',
            reply_markup=get_to_registration_kb(),
        )
        return

    if client.has_trial():
        await msg.answer(
            '🧩 Практики для роста\n\n'
            'Я приготовила для тебя короткий путь внутрь.\n'
            '3 дня — чтобы почувствовать движение.\n'
            'Без напряга. Но с эффектом.\n\n'
            'Если хочешь попробовать — начни сейчас. Это бесплатно.',
            reply_markup=one_button_keyboard(
                text='▶ Начать 3-дневный челлендж',
                callback_data='start_trial_challenge',
            ),
        )
        return

    # TODO: Доделать сообщения в практиках для роста

    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    await answer_func(
        'Выбери, в каком челлендже ты хочешь участвовать',
        reply_markup=await keyboard_from_queryset(
            WeeklyQuest,
            'weekly_quest',
        ),
    )


@router.callback_query(F.data.startswith('weekly_quest'))
async def weekly_quest_detail(query: CallbackQuery):
    quest = await WeeklyQuest.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        quest.title,
        reply_markup=await get_weekly_quest_kb(quest),
    )


@router.callback_query(F.data.startswith('participate_in_weekly_quest'))
@flags.with_client
async def participate_in_weekly_quest(query: CallbackQuery, client: Client):
    quest = await WeeklyQuest.objects.aget(pk=query.data.split(':')[1])
    await ClientWeeklyQuest.objects.acreate(client=client, quest=quest)
    await query.message.edit_text(
        f'Теперь ты участвуешь в челлендже "{quest.title}"!\n'
        f'Я буду присылать тебе новое задание каждый день.',
    )
