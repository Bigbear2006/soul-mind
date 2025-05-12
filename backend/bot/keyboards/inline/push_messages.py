from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_universe_advice_extended_kb(
    universe_advice_text: str,
    personal_day_text: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=universe_advice_text,
                    callback_data='universe_advice',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=personal_day_text,
                    callback_data='personal_day',
                ),
            ],
        ],
    )
