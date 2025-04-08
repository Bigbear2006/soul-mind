from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def one_button_keyboard(
    *,
    back_button_data: str = None,
    **kwargs,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(**kwargs)
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()
