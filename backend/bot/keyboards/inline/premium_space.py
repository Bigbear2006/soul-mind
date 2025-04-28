from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

premium_space_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🚀 Твой День силы',
                callback_data='power_day',
            ),
        ],
        [
            InlineKeyboardButton(
                text='✨ Ответ Вселенной',
                callback_data='universe_answer',
            ),
        ],
        [
            InlineKeyboardButton(
                text='VIP-совет от Soul Muse',
                callback_data='soul_muse_vip_answer',
            ),
        ],
    ],
)
