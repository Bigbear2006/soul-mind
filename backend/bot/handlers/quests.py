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
    get_quests_kb,
    get_weekly_quest_kb,
    get_weekly_quests_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from bot.templates.quests import (
    daily_praises,
    get_daily_quest_text,
    trial_quest_praise,
    weekly_praises,
)
from core.choices import SubscriptionPlans
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
        if client.subscription_plan == SubscriptionPlans.STANDARD:
            await answer_func(
                client.genderize(
                    '🧩 Практики для роста\n'
                    'Ты уже в игре.\n'
                    'Каждый день — одно действие для фокуса.\n'
                    'Каждый месяц — один челлендж, который собирает тебя по частям.\n'
                    'И да, за это ты ещё получаешь астробаллы.\n\n'
                    '{gender:Готов,Готова} вырасти в своём ритме?',
                ),
                reply_markup=get_quests_kb(
                    '⚡ Перейти к заданию дня',
                    '▶ Открыть челлендж месяца',
                ),
            )
        else:
            await answer_func(
                client.genderize(
                    '🧩 Практики для роста\n'
                    'Ты в пространстве без ограничений.\n'
                    'Хочешь идти медленно — иди.\n'
                    'Хочешь глубже — выбирай любой челлендж, хоть сейчас.\n'
                    'Баллы считаются за два в месяц — всё остальное только для души.\n\n'
                    '{gender:Готов,Готова} к новому вызову?',
                ),
                reply_markup=get_quests_kb(
                    '⚡ Сегодняшнее задание',
                    '▶ Выбрать челлендж',
                ),
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


@router.callback_query(F.data == 'weekly_quests')
@flags.with_client
async def weekly_quests(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        'Выбери, в каком челлендже ты хочешь участвовать',
        reply_markup=await get_weekly_quests_kb(client),
    )


@router.callback_query(F.data == 'daily_quest')
@flags.with_client
async def daily_quest(query: CallbackQuery, client: Client):
    quest = await client.get_today_quest()
    if quest.status == QuestStatuses.COMPLETED:
        await query.message.edit_text(
            client.genderize(
                'Сегодня ты уже {gender:выполнил,выполнила} ежедневное задание.\n',
            ),
        )
        return

    await query.message.edit_text(
        get_daily_quest_text(client, quest.quest.text),
        reply_markup=get_quest_statuses_kb(client, 'daily', quest.quest_id),
    )


@router.callback_query(F.data.startswith('weekly_quest'))
@flags.with_client
async def weekly_quest_detail(query: CallbackQuery, client: Client):
    quest = await WeeklyQuest.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        client.genderize(f'{quest.title}\n\n{quest.description}'),
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
            client.genderize(task.to_message_text()),
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

    if quest_type == 'daily':
        await QuestModel.objects.filter(
            client_id=query.message.chat.id,
            quest_id=quest_id,
        ).aupdate(
            status=status,
        )
    else:
        try:
            await QuestModel.objects.acreate(
                client_id=query.message.chat.id,
                quest_id=quest_id,
                status=status,
            )
        except IntegrityError:
            await query.answer(
                client.genderize(
                    'Ты уже {gender:проходил,проходила} это задание',
                ),
            )
            return

    if status == QuestStatuses.COMPLETED:
        await query.message.edit_text(
            client.genderize(random.choice(daily_praises)),
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
