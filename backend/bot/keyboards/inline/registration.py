from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
