from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.utils import keyboard_from_queryset
from core.choices import QuestStatuses
from core.models import Client, QuestTag, WeeklyQuest

def get_quests_kb(daily_quests_text: str, weekly_quests_text: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=daily_quests_text, callback_data='daily_quest')],
            [InlineKeyboardButton(text=weekly_quests_text, callback_data='weekly_quests')],
        ]
    )


async def get_weekly_quests_kb(client: Client):
    return await keyboard_from_queryset(
        WeeklyQuest.objects.filter(
            tags__tag__in=QuestTag.objects.filter(clients__client=client),
        ),
        'weekly_quest',
    )


async def get_weekly_quest_kb(quest: WeeklyQuest):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Участвовать',
                    callback_data=f'participate_in_weekly_quest:{quest.pk}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='weekly_quests',
                ),
            ],
        ],
    )


def get_quest_statuses_kb(
    client: Client,
    quest_type: Literal['daily', 'weekly'],
    task_id: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in QuestStatuses.choices:
        kb.button(
            text=client.genderize(label),
            callback_data=f'quest:{quest_type}:{task_id}:{value}',
        )
    return kb.adjust(1).as_markup()
