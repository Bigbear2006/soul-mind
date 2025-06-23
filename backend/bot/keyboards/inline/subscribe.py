from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.choices import SubscriptionPlans

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


def get_subscription_plan_kb(plan: SubscriptionPlans):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'1 месяц - {plan.price} ₽',
                    callback_data='pay_subscription:1',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'12 месяцев - {plan.price * 8} ₽',
                    callback_data='pay_subscription:12',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='subscription_plans',
                ),
            ],
        ],
    )
