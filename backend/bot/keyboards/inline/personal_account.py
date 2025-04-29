from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_personal_account_kb(subscription_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Мои подарки',
                    callback_data='personal_gifts',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Мои инсайты',
                    callback_data='personal_insights',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=subscription_text,
                    callback_data='subscription_plans',
                ),
            ],
        ],
    )
