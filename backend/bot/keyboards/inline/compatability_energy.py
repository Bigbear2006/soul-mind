from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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


def get_buy_compatability_kb(back_button_data: str | None = None):
    kb = InlineKeyboardBuilder.from_markup(
        InlineKeyboardMarkup(
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
        ),
    )
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()


trial_usages_ended_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🌟 Оформить подписку',
                callback_data='subscription_plans_with_back_button',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🔓 Разблокировать доп. совместимости',
                callback_data='buy_compatability_choices',
            ),
        ],
    ],
)
