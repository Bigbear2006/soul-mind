from collections.abc import Callable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices, Model, QuerySet

from bot.settings import settings


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


async def get_pagination_buttons(
    previous_button_data: str = None,
    next_button_data: str = None,
) -> list[InlineKeyboardButton]:
    pagination_buttons = []

    if previous_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<<',
                callback_data=previous_button_data,
            ),
        )

    if next_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(text='>>', callback_data=next_button_data),
        )

    return pagination_buttons


async def keyboard_from_queryset(
    queryset: QuerySet,
    prefix: str,
    *,
    str_func: Callable[[Model], str] | None = None,
    back_button_data: str | None = None,
    previous_button_data: str | None = None,
    next_button_data: str | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    str_func = str_func or str

    async for obj in queryset:
        kb.button(text=str_func(obj), callback_data=f'{prefix}:{obj.pk}')

    kb.adjust(1)
    kb.row(
        *await get_pagination_buttons(
            previous_button_data,
            next_button_data,
        ),
    )

    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)

    return kb.adjust(1).as_markup()


async def get_paginated_keyboard(
    queryset: Callable[[], QuerySet],
    *,
    prefix: str = '',
    page: int = 1,
    str_func: Callable[[Model], str] | None = None,
    back_button_data: str = None,
    previous_button_data: str = 'consults_previous',
    next_button_data: str = 'consults_next',
) -> InlineKeyboardMarkup:
    total_count = await queryset().acount()
    total_pages = (total_count + settings.PAGE_SIZE - 1) // settings.PAGE_SIZE
    start, end = (page - 1) * settings.PAGE_SIZE, page * settings.PAGE_SIZE
    queryset = queryset()[start:end]

    return await keyboard_from_queryset(
        queryset,
        prefix=prefix,
        str_func=str_func,
        back_button_data=back_button_data,
        previous_button_data=previous_button_data if page > 1 else None,
        next_button_data=next_button_data if page < total_pages else None,
    )


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
