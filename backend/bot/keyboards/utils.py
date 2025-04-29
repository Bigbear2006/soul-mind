from collections.abc import Callable

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices, Model


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


async def keyboard_from_queryset(
    model: type[Model],
    prefix: str,
    *,
    filters: dict | None = None,
    str_func: Callable[[Model], str] | None = None,
    back_button_data: str = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    filters = filters or {}
    str_func = str_func or str

    async for obj in model.objects.filter(**filters):
        kb.button(text=str_func(obj), callback_data=f'{prefix}:{obj.pk}')

    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)

    return kb.adjust(1).as_markup()


def keyboard_from_choices(
    choices: type[Choices],
    *,
    prefix: str = '',
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in choices.choices:
        kb.button(
            text=label,
            callback_data=f'{prefix}:{value}' if prefix else value,
        )
    return kb.adjust(1).as_markup()
