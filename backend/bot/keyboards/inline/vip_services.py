from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Case, IntegerField, Subquery, Value, When

from bot.keyboards.utils import (
    get_paginated_keyboard,
    keyboard_from_queryset,
    one_button_keyboard,
)
from core.choices import MiniConsultStatuses
from core.models import Client, ClientExpertType, MiniConsult, Topic

vip_services_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Мини-консультация с экспертом',
                callback_data='vip_mini_consult',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Глубокий персональный отчёт',
                callback_data='vip_personal_report',
            ),
        ],
        [
            InlineKeyboardButton(
                text='VIP-анализ совместимости',
                callback_data='vip_compatibility',
            ),
        ],
        [InlineKeyboardButton(text='В меню', callback_data='to_menu')],
    ],
)

connection_types_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='💞 Пара (романтическая)',
                callback_data='connection_type:couple',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🏡 Семья',
                callback_data='connection_type:family',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🤝 Друзья',
                callback_data='connection_type:friends',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🚀 Команда / бизнес / коллеги',
                callback_data='connection_type:team',
            ),
        ],
    ],
)


def get_payment_choices_kb(
    astropoints: str | None,
    money: str | None,
    *,
    back_button_data: str | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if astropoints:
        kb.button(text=astropoints, callback_data='astropoints')
    if money:
        kb.button(text=money, callback_data='money')
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()


async def get_topics_kb(client: Client):
    kb = InlineKeyboardBuilder.from_markup(
        await keyboard_from_queryset(
            Topic.objects.filter(is_global=True),
            prefix='topic',
            str_func=lambda x: client.genderize(str(x)),
        ),
    )
    kb.button(text='Я выбрал нужные метки', callback_data='topic:done')
    return kb.adjust(1).as_markup()


def get_vip_compatability_report_kb(
    add_person_btn: bool,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if add_person_btn:
        kb.button(text='Добавить человека', callback_data='add_person')
    kb.button(text='Получить отчет', callback_data='vip_compatability_report')
    return kb.adjust(1).as_markup()


async def get_consults_list_kb(client: Client, page: int = 1):
    return await get_paginated_keyboard(
        lambda: (
            MiniConsult.objects.filter(
                status=MiniConsultStatuses.WAITING,
                expert_type__in=Subquery(
                    ClientExpertType.objects.filter(client=client).values(
                        'expert_type',
                    ),
                ),
            )
            .select_related('client')
            .annotate(
                sort_order=Case(
                    When(client__subscription_plan='premium', then=Value(1)),
                    When(client__subscription_plan='standard', then=Value(2)),
                    When(client__subscription_plan='', then=Value(3)),
                    default=Value(4),
                    output_field=IntegerField(),
                ),
            )
            .order_by('sort_order', 'date')
        ),
        prefix='mini_consult',
        str_func=lambda x: x.to_button_text(),
        page=page,
    )


def get_answer_consult_kb(
    consult_id: int,
    back_button_data: str | None = None,
):
    return one_button_keyboard(
        text='Ответить',
        callback_data=f'answer_consult:{consult_id}',
        back_button_data=back_button_data,
    )


def get_end_consult_kb(consult_id: int, back_button_data: str | None = None):
    return one_button_keyboard(
        text='Завершить консультацию',
        callback_data=f'end_consult:{consult_id}',
        back_button_data=back_button_data,
    )
