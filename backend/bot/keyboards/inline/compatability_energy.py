from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

compatability_energy_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Вместе', callback_data='together')],
        [InlineKeyboardButton(text='Нравится', callback_data='like')],
        [InlineKeyboardButton(text='Бывшие', callback_data='past_lovers')],
    ],
)

show_connection_depth = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='💎 Узнать глубину связи – 1599 ₽ / 2500 баллов',
                callback_data='show_connection_depth',
            ),
        ],
    ],
)

buy_compatability_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='1 совместимость',
                callback_data='buy_compatability:one',
            ),
        ],
        [
            InlineKeyboardButton(
                text='3 совместимости',
                callback_data='buy_compatability:three',
            ),
        ],
        [
            InlineKeyboardButton(
                text='VIP-анализ совместимости',
                callback_data='show_connection_depth',
            ),
        ],
    ],
)
