from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.choices import QuestStatuses
from core.models import WeeklyQuest


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
                    callback_data='to_weekly_quests_list',
                ),
            ],
        ],
    )


def get_quest_statuses_kb(
    quest_type: Literal['daily', 'weekly'],
    quest_id: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in QuestStatuses.choices:
        kb.button(
            text=label,
            callback_data=f'quest:{quest_type}:{quest_id}:{value}',
        )
    return kb.adjust(1).as_markup()
