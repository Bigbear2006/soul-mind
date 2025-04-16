from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices

from core.models import QuestStatuses, WeeklyQuest

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

start_ways_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✨ Погрузи меня сразу',
                callback_data='start_way_right_now',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🔎 Объясни, как это работает',
                callback_data='start_way_explain',
            ),
        ],
    ],
)

birth_times_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Утро (06:00–10:59)',
                callback_data='birth_time_08:00',
            ),
            InlineKeyboardButton(
                text='День (11:00–15:59)',
                callback_data='birth_time_13:00',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Вечер (16:00–20:59)',
                callback_data='birth_time_18:00',
            ),
            InlineKeyboardButton(
                text='Ночь (21:00–01:59)',
                callback_data='birth_time_23:00',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Раннее утро (02:00–05:59)',
                callback_data='birth_time_04:00',
            ),
            InlineKeyboardButton(
                text='Вообще не знаю',
                callback_data='birth_time_12:00',
            ),
        ],
    ],
)

notifications_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔔 Да, получать послания',
                callback_data='notifications:yes',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🙂 Пока нет',
                callback_data='notifications:no',
            ),
        ],
    ],
)

to_registration_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔓 Разблокировать',
                callback_data='to_registration',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='to_personal_analysis',
            ),
        ],
    ],
)

to_subscription_plans_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔓 Разблокировать',
                callback_data='subscription_plans',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='to_personal_analysis',
            ),
        ],
    ],
)

back_to_personal_analysis_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='to_personal_analysis',
            ),
        ],
    ],
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
                    callback_data='to_weekly_quests_list',
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
