from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

friday_gift_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Сохранить',
                callback_data='save_friday_gift',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Откликнуться',
                callback_data='respond_to_friday_gift',
            ),
        ],
    ],
)
