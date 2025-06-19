import asyncio
import calendar
import functools
import random
from collections.abc import AsyncIterable
from datetime import datetime, timedelta

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Count,
    Exists,
    F,
    Max,
    OuterRef,
    Q,
)
from django.utils.timezone import now

from bot.keyboards.inline.quests import get_quest_statuses_kb
from bot.keyboards.utils import one_button_keyboard
from bot.loader import bot
from bot.services.numerology import get_power_day
from bot.settings import settings
from bot.text_templates.push_messages import (
    destiny_guide,
    friday_gift,
    new_weekly_quest_is_available,
    two_days_before_power_day,
    universe_advice,
    universe_advice_extended,
    universe_advice_extended_reminder,
    universe_advice_reminder,
)
from bot.text_templates.quests import quest_reminder
from core.choices import Actions, QuestStatuses
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


async def dispatch_messages(
    clients_ids: AsyncIterable[int],
    text: str,
    **kwargs,
):
    await asyncio_wait(
        [
            asyncio.create_task(safe_send_message(cid, text, **kwargs))
            async for cid in clients_ids
        ],
    )


async def dispatch_genderized_messages(
    clients: AsyncIterable[Client],
    text: str,
    **kwargs,
):
    await asyncio_wait(
        [
            asyncio.create_task(
                safe_send_message(c.pk, c.genderize(text), **kwargs),
            )
            async for c in clients
        ],
    )


def async_shared_task(func):
    @shared_task
    @functools.wraps(func)
    def decorator():
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        loop.run_until_complete(func())

    return decorator


async def send_daily_quest(
    client: Client,
    quests_ids: set,
    sent_quests_ids: list,
):
    try:
        quest = await DailyQuest.objects.aget(
            pk=random.choice(list(set(quests_ids) - set(sent_quests_ids))),
        )
    except IndexError:
        return

    await safe_send_message(
        client.pk,
        client.genderize(
            '🧩 Задание дня от Soul Muse\n'
            'Сегодня — маленький шаг к себе.\n'
            'Быстрый. Точный. Не ради галочки, а ради фокуса.\n\n'
            'Хочешь почувствовать, что день не просто начался, а начался по-твоему?\n'
            f'Вот задание:\n\n{quest.text}',
        ),
        reply_markup=get_quest_statuses_kb(client, 'daily', quest.pk),
    )


@async_shared_task
async def send_daily_quests():
    today = now()
    quests_ids = await sync_to_async()(
        lambda: set(DailyQuest.objects.values_list('id', flat=True)),
    )()

    quests = (
        ClientDailyQuest.objects.select_related('client')
        .filter(
            client__notifications_enabled=True,
            client__subscription_end__gte=today,
            quest__is_active=True,
        )
        .annotate(sent_quests_ids=ArrayAgg('quest_id'))
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_daily_quest(
                    quest.client,
                    quests_ids,
                    quest.sent_quests_ids,
                ),
            )
            async for quest in quests
        ],
    )

    clients = (
        Client.objects.only('id', 'gender')
        .annotate(sent_quests_count=Count('daily_quests'))
        .filter(
            sent_quests_count=0,
            notifications_enabled=True,
            subscription_end__gte=today,
        )
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_daily_quest(
                    client,
                    quests_ids,
                    [],
                ),
            )
            async for client in clients
        ],
    )


async def send_weekly_quest_task(client: Client, quest_task_id: int, day: int):
    try:
        quest = await WeeklyQuestTask.objects.select_related('quest').aget(
            quest_id=quest_task_id,
            day=day,
        )
    except ObjectDoesNotExist:
        task_logger.info(
            f'WeeklyQuestTask does not exists {quest_task_id=} {day=}',
        )
        return

    await safe_send_message(
        client.pk,
        client.genderize(quest.to_message_text()),
        reply_markup=get_quest_statuses_kb(client, 'weekly', quest.pk),
    )


@async_shared_task
async def send_weekly_quests_tasks():
    tasks = (
        ClientWeeklyQuestTask.objects.annotate(
            quest_task_id=F('quest__quest_id'),
            day=F('quest__day'),
        )
        .values('client_id', 'quest_task_id')
        .annotate(
            last_completed_day=Max(
                'day',
                filter=Q(status=QuestStatuses.COMPLETED),
                default=0,
            ),
        )
        .filter(
            (
                Q(last_completed_day__lt=7)
                & ~Q(quest_task_id=settings.TRIAL_WEEKLY_QUEST_ID)
            )
            | Q(
                last_completed_day__lt=3,
                quest_task_id=settings.TRIAL_WEEKLY_QUEST_ID,
            ),
            quest__is_active=True,
            client__notifications_enabled=True,
        )
    )

    client_ids = {task['client_id'] async for task in tasks}
    clients = {
        client.id: client
        async for client in Client.objects.filter(id__in=client_ids)
    }
    [task_logger.info(str(i)) async for i in tasks]

    await asyncio_wait(
        [
            asyncio.create_task(
                send_weekly_quest_task(
                    clients[task['client_id']],
                    task['quest_task_id'],
                    task['last_completed_day'] + 1,
                ),
            )
            async for task in tasks
        ],
    )

    clients = (
        ClientWeeklyQuest.objects.prefetch_related('client')
        .filter(
            quest__is_active=True,
            client__notifications_enabled=True,
        )
        .exclude(
            Exists(
                ClientWeeklyQuestTask.objects.filter(
                    quest__quest_id=OuterRef('quest_id'),
                    client_id=OuterRef('client_id'),
                ),
            ),
        )
    )

    await asyncio_wait(
        [
            asyncio.create_task(
                send_weekly_quest_task(
                    client.client,
                    client.quest_id,
                    1,
                ),
            )
            async for client in clients
        ],
    )


@async_shared_task
async def send_quests_reminders():
    today = now()
    clients_ids = Client.objects.filter(
        ~Q(
            id__in=ClientDailyQuest.objects.filter(
                ~Q(status=''),
                created_at__date=today.date(),
            ).values_list('client_id', flat=True),
        ),
        notifications_enabled=True,
        subscription_end__gte=today,
    )
    kb = one_button_keyboard(text='⚡ Сегодняшнее задание', callback_data='daily_quest')
    await dispatch_genderized_messages(clients_ids, quest_reminder, reply_markup=kb)


@async_shared_task
async def send_new_weekly_quest_is_available():
    date = now()
    clients = Client.objects.filter(
        notifications_enabled=True,
        created_at__lte=date - timedelta(days=3),
        subscription_end__lte=date,
    )

    await dispatch_genderized_messages(
        clients,
        new_weekly_quest_is_available['text'],
        reply_markup=new_weekly_quest_is_available['reply_markup'],
    )


def get_universe_advice_text_and_kb(
    today: datetime,
    *,
    extended: bool,
) -> tuple[str, InlineKeyboardMarkup]:
    day_type = 'weekday' if today.weekday() < 5 else 'weekend'
    advice = universe_advice_extended if extended else universe_advice
    reminder = (
        universe_advice_extended_reminder
        if extended
        else universe_advice_reminder
    )

    if today.hour < 11:  # UTC
        return (
            random.choice(advice['text'][day_type]),
            advice['reply_markup'][day_type],
        )

    return (
        random.choice(reminder['text']),
        reminder['reply_markup'],
    )


@async_shared_task
async def send_universe_advice_messages():
    today = now()
    clients = (
        Client.objects.filter(
            notifications_enabled=True,
            created_at__lte=today - timedelta(days=3),
            subscription_end__lte=today,
        )
        .exclude(
            actions__action=Actions.UNIVERSE_ADVICE,
            actions__date__date=today.date(),
        )
        .distinct()
    )
    text, kb = get_universe_advice_text_and_kb(today, extended=False)
    await dispatch_genderized_messages(clients, text, reply_markup=kb)


@async_shared_task
async def send_university_advice_extended_messages():
    today = now()
    clients = (
        Client.objects.annotate_actions(today.date())
        .filter(
            Q(created_at__gte=today - timedelta(days=3))
            | Q(subscription_end__gte=today),
            notifications_enabled=True,
            universe_advice_count=0,
            personal_day_count=0,
        )
        .distinct()
    )
    text, kb = get_universe_advice_text_and_kb(today, extended=True)
    await dispatch_genderized_messages(clients, text, reply_markup=kb)


@async_shared_task
async def send_destiny_guide_messages():
    today = now().date()
    first_week_day = now() - timedelta(days=today.weekday())
    last_week_day = now() + timedelta(days=6)
    clients = (
        Client.objects.filter(notifications_enabled=True)
        .exclude(
            actions__action=Actions.DESTINY_GUIDE,
            actions__date__date__gte=first_week_day,
            actions__date__date__lte=last_week_day,
        )
        .distinct()
    )
    n = random.randint(0, 3)
    await dispatch_genderized_messages(
        clients,
        destiny_guide['text'][n],
        reply_markup=destiny_guide['reply_markup'][n],
    )


@async_shared_task
async def send_friday_gift_messages():
    clients = Client.objects.filter(notifications_enabled=True)
    n = random.randint(0, 3)
    await dispatch_genderized_messages(
        clients,
        friday_gift['text'][n],
        reply_markup=friday_gift['reply_markup'][n],
    )


@async_shared_task
async def send_power_day_messages():
    today = now().date()
    clients = Client.objects.filter(notifications_enabled=True)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    clients_ids = []
    async for client in clients:
        day = get_power_day(client.birth.date())
        if day > days_in_month:
            day -= days_in_month
        if day - 2 == today.day:
            clients_ids.append(client.pk)

    await asyncio_wait(
        [
            asyncio.create_task(
                safe_send_message(cid, two_days_before_power_day),
            )
            for cid in clients_ids
        ],
    )
