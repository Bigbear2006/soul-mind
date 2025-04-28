from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_to_registration_kb(
    *,
    text='🔓 Разблокировать',
    back_button_data: str = None,
):
    kb = InlineKeyboardBuilder()
    kb.button(text=text, callback_data='to_registration')
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()


def get_to_subscription_plans_kb(
    *,
    text='🔓 Разблокировать',
    back_button_data: str = None,
):
    kb = InlineKeyboardBuilder()
    kb.button(text=text, callback_data='subscription_plans')
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()
