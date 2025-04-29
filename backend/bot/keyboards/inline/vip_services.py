from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.utils import keyboard_from_queryset
from core.models import Topic

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
    astropoints: str,
    money: str,
    *,
    back_button_data: str | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=astropoints, callback_data='astropoints')
    kb.button(text=money, callback_data='money')
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return kb.adjust(1).as_markup()


async def get_topics_kb():
    kb = InlineKeyboardBuilder.from_markup(
        await keyboard_from_queryset(
            Topic,
            prefix='topic',
            filters={'is_global': True},
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
