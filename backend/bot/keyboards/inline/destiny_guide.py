from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.utils import one_button_keyboard

destiny_guide_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🪐 Астрособытия месяца',
                callback_data='destiny_guide',
            ),
        ],
        [
            InlineKeyboardButton(
                text='📍 Важные дни',
                callback_data='important_days',
            ),
        ],
    ],
)

to_destiny_guide_kb = one_button_keyboard(
    text='Назад',
    callback_data='destiny_guide_intro',
)
