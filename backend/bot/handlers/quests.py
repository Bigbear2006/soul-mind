import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async
from django.db import IntegrityError, models

from bot.keyboards.inline import get_quest_statuses_kb
from core.models import (
    Client,
    ClientDailyQuest,
    ClientWeeklyQuestTask,
    DailyQuest,
    QuestStatuses,
    WeeklyQuestTask,
)

router = Router()


@router.callback_query(F.data.startswith('quest'))
async def quest_handler(query: CallbackQuery):
    astropoints = 10
    _, quest_type, quest_id, status = query.data.split(':')
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

    if status == QuestStatuses.COMPLETED and quest_type == 'weekly':
        weekly_quest_task = await WeeklyQuestTask.objects.select_related(
            'quest',
        ).aget(
            quest_id=quest_id,
        )
        if weekly_quest_task.day == 7:
            astropoints += 10
            await query.message.answer(
                f'Поздравляем, Вы полностью прошли 7-дневный челлендж '
                f'{weekly_quest_task.quest}!\n'
                f'За это вам начислено еще +10 астробаллов!',
            )

    if status == QuestStatuses.COMPLETED:
        await Client.objects.filter(pk=query.message.chat.id).aupdate(
            astropoints=models.F('astropoints') + astropoints,
        )

    str_status = (
        'выполнили' if status == QuestStatuses.COMPLETED else 'пропустили'
    )
    await query.message.edit_text(
        f'Вы {str_status} задание\n' + query.message.text,
        reply_markup=None,
    )


@router.message(Command('daily_quest'))
async def send_daily_quest_handler(msg: Message):
    quests_ids = await sync_to_async(list)(
        DailyQuest.objects.values_list('id', flat=True),
    )
    quest = await DailyQuest.objects.aget(pk=random.choice(quests_ids))
    await msg.answer(
        f'Ежедневный челлендж\n\n{quest.text}',
        reply_markup=get_quest_statuses_kb('daily', quest.pk),
    )


@router.message(Command('weekly_quest'))
async def send_weekly_quest_handler(msg: Message):
    quest = (
        await WeeklyQuestTask.objects.filter(day=7)
        .select_related('quest')
        .afirst()
    )
    await msg.answer(
        f'{quest.quest.title} (день {quest.day})\n\n{quest.text}',
        reply_markup=get_quest_statuses_kb('weekly', quest.pk),
    )
