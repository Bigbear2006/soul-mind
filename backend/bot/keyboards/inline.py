from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.models import SubscriptionPlanChoices

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


def get_subscription_plans_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in SubscriptionPlanChoices.choices:
        kb.button(text=label, callback_data=value)
    return kb.adjust(1).as_markup()
