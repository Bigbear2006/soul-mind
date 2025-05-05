import random

from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message
from django.db import IntegrityError, models

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.quests import (
    get_weekly_quest_kb,
)
from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.settings import settings
from bot.templates.quests import daily_praises, weekly_praises
from core.models import (
    Client,
    ClientDailyQuest,
    ClientWeeklyQuest,
    ClientWeeklyQuestTask,
    QuestStatuses,
    WeeklyQuest,
    WeeklyQuestTask,
)

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


@router.callback_query(
    F.data.startswith('participate_in_weekly_quest') | F.data
    == 'start_trial_challenge',
)
@flags.with_client
async def participate_in_weekly_quest(query: CallbackQuery, client: Client):
    pk = (
        query.data.split(':')[1]
        if query.data.startswith('participate_in_weekly_quest')
        else settings.TRIAL_WEEKLY_QUEST_ID
    )
    try:
        quest = await WeeklyQuest.objects.aget(pk=pk)
        await ClientWeeklyQuest.objects.acreate(client=client, quest=quest)
        await query.message.edit_text(
            f'Теперь ты участвуешь в челлендже {quest.title}!\n'
            f'Я буду присылать тебе новое задание каждый день.',
        )
    except IntegrityError:
        await query.message.edit_text('Ты уже участвуешь в этом челлендже.')


@router.callback_query(F.data.startswith('quest'))
async def quest_handler(query: CallbackQuery):
    _, quest_type, quest_id, status = query.data.split(':')
    astropoints = 5 if quest_type == 'daily' else 10
    QuestModel = (
        ClientDailyQuest if quest_type == 'daily' else ClientWeeklyQuestTask
    )

    try:
        await QuestModel.objects.acreate(
            client_id=query.message.chat.id,
            quest_id=quest_id,
            status=status,
        )
    except IntegrityError:
        await query.answer('Вы уже проходили это задание')
        return

    if status == QuestStatuses.COMPLETED:
        await query.message.edit_text(
            random.choice(daily_praises),
            reply_markup=None,
        )
    else:
        await query.message.edit_text(
            'Задание пропущено',
            reply_markup=None,
        )

    if status == QuestStatuses.COMPLETED and quest_type == 'weekly':
        weekly_quest_task = await WeeklyQuestTask.objects.select_related(
            'quest',
        ).aget(quest_id=quest_id)
        if weekly_quest_task.day == 7:
            astropoints += 10
            await query.message.edit_text(random.choice(weekly_praises))

        if weekly_quest_task.pk == settings.TRIAL_WEEKLY_QUEST_ID:
            astropoints += 10
            await query.message.edit_text(
                '“Ты сделал(а) три шага внутрь. Это не всё. Это только начало.”\n\n'
                'Ты почувствовал(а), каково это — быть с собой.\n'
                'Не снаружи. А внутри.\n'
                'Без давления. Без роли.\n'
                'Ты не начал(а) путь самопознания — ты вернулся(лась) к себе.\n'
                'А дальше?..\n'
                'Дальше — глубже. Точнее. Свободнее.\n'
                'SoulMind приготовил для тебя десятки векторов:\n'
                'эмоциональный интеллект, осознанность, энергия…\n'
                'Что дальше?\n'
                'Внутри тебя ждёт:\n'
                '— 300+ практик по твоим внутренним точкам роста\n'
                '— 23 темы: от самоценности и границ до отпускания и завершения\n'
                '— Челленджи, собранные под твой уникальный путь\n'
                'Это не “мотивация”. Это SoulMind.\n'
                'Ты готов(а)? Тогда заходи глубже.\n'
                '“Я не скажу тебе, кто ты. Я помогу тебе вспомнить.” — Soul Muse',
                reply_markup=get_to_subscription_plans_kb(
                    text='Оформить подписку',
                ),
            )

    if status == QuestStatuses.COMPLETED:
        await Client.objects.filter(pk=query.message.chat.id).aupdate(
            astropoints=models.F('astropoints') + astropoints,
        )


# @router.message(Command('daily_quest'))
# async def send_daily_quest_handler(msg: Message):
#     quests_ids = await sync_to_async(list)(
#         DailyQuest.objects.values_list('id', flat=True),
#     )
#     quest = await DailyQuest.objects.aget(pk=random.choice(quests_ids))
#     await msg.answer(
#         f'Ежедневный челлендж\n\n{quest.text}',
#         reply_markup=get_quest_statuses_kb('daily', quest.pk),
#     )
#
#
# @router.message(Command('weekly_quest'))
# async def send_weekly_quest_handler(msg: Message):
#     quest = (
#         await WeeklyQuestTask.objects.filter(day=7)
#         .select_related('quest')
#         .afirst()
#     )
#     await msg.answer(
#         f'{quest.quest.title} (день {quest.day})\n\n{quest.text}',
#         reply_markup=get_quest_statuses_kb('weekly', quest.pk),
#     )
