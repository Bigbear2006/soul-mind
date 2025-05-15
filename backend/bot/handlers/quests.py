import random

from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message
from django.db import IntegrityError, models

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.quests import (
    get_quest_statuses_kb,
    get_weekly_quest_kb,
    get_weekly_quests_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from bot.templates.quests import (
    daily_praises,
    trial_quest_praise,
    weekly_praises,
)
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
    elif client.subscription_is_active():
        answer_func = (
            msg.answer if isinstance(msg, Message) else msg.message.edit_text
        )
        await answer_func(
            'Выбери, в каком челлендже ты хочешь участвовать',
            reply_markup=await get_weekly_quests_kb(client),
        )
    elif client.has_trial():
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
    else:
        await msg.answer(
            '🧩 Практики для роста доступны в подписке.',
            reply_markup=get_to_subscription_plans_kb(),
        )


@router.callback_query(F.data.startswith('weekly_quest'))
async def weekly_quest_detail(query: CallbackQuery):
    quest = await WeeklyQuest.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        quest.title,
        reply_markup=await get_weekly_quest_kb(quest),
    )


@router.callback_query(
    F.data.startswith('participate_in_weekly_quest')
    | (F.data == 'start_trial_challenge'),
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
        task = await WeeklyQuestTask.objects.select_related('quest').aget(
            quest=quest,
            day=1,
        )
        await ClientWeeklyQuest.objects.acreate(client=client, quest=quest)
        await query.message.edit_text(
            f'Теперь ты участвуешь в челлендже {quest.title}!\n'
            f'Я буду присылать тебе новое задание каждый день.',
        )
        await query.message.answer(
            task.to_message_text(),
            reply_markup=get_quest_statuses_kb(client, 'weekly', task.pk),
        )
    except IntegrityError:
        await query.message.edit_text(
            'Ты уже участвуешь в этом челлендже.\n'
            'Я буду присылать тебе новое задание каждый день.',
        )


@router.callback_query(F.data.startswith('quest'))
@flags.with_client
async def quest_handler(query: CallbackQuery, client: Client):
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
        ).aget(id=quest_id)
        if weekly_quest_task.day == 7:
            astropoints += 10
            await query.message.edit_text(random.choice(weekly_praises))

        if (
            weekly_quest_task.pk == settings.TRIAL_WEEKLY_QUEST_ID
            and weekly_quest_task.day == 3
        ):
            astropoints += 10
            await query.message.edit_text(
                client.genderize(trial_quest_praise),
                reply_markup=get_to_subscription_plans_kb(
                    text='Оформить подписку',
                ),
            )

    if status == QuestStatuses.COMPLETED:
        await Client.objects.filter(pk=query.message.chat.id).aupdate(
            astropoints=models.F('astropoints') + astropoints,
        )
