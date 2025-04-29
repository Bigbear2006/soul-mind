from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

friday_gift_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Откликнуться',
                callback_data='respond_to_friday_gift',
            ),
        ],
    ],
)
