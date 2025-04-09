from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices

from core.models import QuestStatuses

personal_analysis_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔮 Тайна твоего предназначения',
                callback_data='destiny_mystery',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🚀 Карьера и финансы',
                callback_data='career_and_finance',
            ),
        ],
        [
            InlineKeyboardButton(
                text='❤ Твой код любви',
                callback_data='love_code',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🎲 Твой код удачи',
                callback_data='luck_code',
            ),
        ],
        [
            InlineKeyboardButton(
                text='⚡ Твоя суперсила',
                callback_data='superpower',
            ),
        ],
        [
            InlineKeyboardButton(
                text='✨ Твой полный профиль',
                callback_data='full_profile',
            ),
        ],
    ],
)


def keyboard_from_choices(choices: type[Choices]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in choices.choices:
        kb.button(text=label, callback_data=value)
    return kb.adjust(1).as_markup()


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
