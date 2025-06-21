from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

pay_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Я оплатил',
                callback_data='check_buying',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_buying',
            ),
        ],
    ],
)
