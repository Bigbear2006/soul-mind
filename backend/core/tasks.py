import asyncio
import functools
import random
from datetime import timedelta

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from asgiref.sync import sync_to_async
from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, Exists, Max, OuterRef
from django.utils.timezone import now

from bot.keyboards.inline.quests import get_quest_statuses_kb
from bot.loader import bot
from bot.templates.quests import quest_reminder
from core.models import (
    Client,
    ClientDailyQuest,
    ClientWeeklyQuest,
    ClientWeeklyQuestTask,
    DailyQuest,
    WeeklyQuestTask,
)

task_logger = get_task_logger(__name__)


def handle_send_message_errors(send_message_func):
    async def decorator(chat_id: int | str, text: str, **kwargs):
        try:
            await send_message_func(chat_id, text, **kwargs)
        except TelegramRetryAfter as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of rate limit',
            )
            await asyncio.sleep(e.retry_after)
            await send_message_func(chat_id, text, **kwargs)
        except TelegramBadRequest as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of an {e.__class__.__name__} error: {str(e)}',
            )

    return decorator


@handle_send_message_errors
async def safe_send_message(chat_id: int | str, text: str, **kwargs):
    return await bot.send_message(chat_id, text, **kwargs)


async def asyncio_wait(
    fs,
    *,
    timeout=None,
    return_when=asyncio.ALL_COMPLETED,
) -> tuple[set, set]:
    if not fs:
        return set(), set()
    return await asyncio.wait(fs, timeout=timeout, return_when=return_when)


def async_shared_task(func):
    @shared_task
    @functools.wraps(func)
    def decorator():
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        loop.run_until_complete(func())

    return decorator


async def send_daily_quest(client_id: int, quests_ids: set, sent_quests_ids):
    try:
        quest = await DailyQuest.objects.aget(
            pk=random.choice(list(set(quests_ids) - set(sent_quests_ids))),
        )
    except IndexError:
        return

    await safe_send_message(
        client_id,
        '🧩 Задание дня от Soul Muse\n'
        'Сегодня — маленький шаг к себе.\n'
        'Быстрый. Точный. Не ради галочки, а ради фокуса.\n\n'
        'Хочешь почувствовать, что день не просто начался, а начался по-твоему?\n'
        f'Вот задание:\n\n{quest.text}',
        reply_markup=get_quest_statuses_kb('daily', quest.pk),
    )


@async_shared_task
async def send_daily_quests():
    quests_ids = await sync_to_async()(
        lambda: set(DailyQuest.objects.values_list('id', flat=True)),
    )()

    quests = (
        ClientDailyQuest.objects.filter(
            created_at__gte=now() - timedelta(days=30),
            client__notifications_enabled=True,
            quest__is_active=True,
        )
        .values('client_id')
        .annotate(sent_quests_ids=ArrayAgg('quest_id'))
        .order_by('client_id')
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_daily_quest(
                    quest['client_id'],
                    quests_ids,
                    quest['sent_quests_ids'],
                ),
            )
            async for quest in quests
        ],
    )

    clients_ids = (
        Client.objects.annotate(sent_quests_count=Count('daily_quests'))
        .filter(
            sent_quests_count=0,
            notifications_enabled=True,
        )
        .values_list('id', flat=True)
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_daily_quest(
                    client_id,
                    quests_ids,
                    {},
                ),
            )
            async for client_id in clients_ids
        ],
    )


async def send_weekly_quest_task(client_id: int, quest_task_id: int, day: int):
    quest = await WeeklyQuestTask.objects.select_related('quest').aget(
        quest_id=quest_task_id,
        day=day,
    )
    await safe_send_message(
        client_id,
        f'{quest.quest.title} (день {quest.day})\n\n'
        f'{quest.title}\n{quest.text}',
        reply_markup=get_quest_statuses_kb('weekly', quest.pk),
    )


@async_shared_task
async def send_weekly_quests_tasks():
    tasks = (
        ClientWeeklyQuestTask.objects.annotate(last_task_day=Max('quest__day'))
        .filter(
            notifications_enabled=True,
            last_task_day__lt=7,
        )
        .values('client_id', 'quest_id')
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_weekly_quest_task(
                    task['client_id'],
                    task['quest__quest_id'],
                    task['last_task_day'] + 1,
                ),
            )
            async for task in tasks
        ],
    )

    clients = (
        ClientWeeklyQuest.objects.filter(client__notifications_enabled=True)
        .exclude(
            Exists(
                ClientWeeklyQuestTask.objects.filter(
                    quest__quest_id=OuterRef('quest_id'),
                    client_id=OuterRef('client_id'),
                ),
            ),
        )
        .values_list('client_id', 'quest__quest_id')
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_weekly_quest_task(
                    client['client_id'],
                    client['quest_id'],
                    1,
                ),
            )
            async for client in clients
        ],
    )


@async_shared_task
async def send_quests_reminders():
    clients_ids = (
        Client.objects.filter(notifications_enabled=True)
        .exclude(
            id__in=ClientDailyQuest.objects.filter(
                created_at__day=now().day,
            ).values_list('client_id', flat=True),
        )
        .values_list('id', flat=True)
    )
    await asyncio_wait(
        [
            asyncio.create_task(safe_send_message(client_id, quest_reminder))
            async for client_id in clients_ids
        ],
    )


@async_shared_task
async def send_university_advice_messages():
    pass


@async_shared_task
async def send_university_advice_reminders():
    pass


@async_shared_task
async def send_university_advice_extended_messages():
    pass


@async_shared_task
async def send_university_advice_extended_reminders():
    pass


@async_shared_task
async def send_destiny_guide_messages():
    pass


@async_shared_task
async def send_friday_gift_messages():
    pass


@async_shared_task
async def send_power_day_messages():
    pass
