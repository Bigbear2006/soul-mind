from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

universe_advice_extended_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🌟 Открыть совет',
                callback_data='university_advice',
            ),
        ],
        [
            InlineKeyboardButton(
                text='📆 Узнать свой день',
                callback_data='personal_day',
            ),
        ],
    ],
)
