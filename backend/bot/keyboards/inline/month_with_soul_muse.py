from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

month_with_soul_muse_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🎁 Персональный прогноз на месяц',
                callback_data='month_forecast',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🎁 Главный ресурс месяца',
                callback_data='month_main_resource',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🎁 Твой сценарий месяца',
                callback_data='month_script',
            ),
        ],
    ],
)
