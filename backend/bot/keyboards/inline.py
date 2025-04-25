from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices

from bot.handlers.vip_services import vip_compatibility
from core.models import QuestStatuses, WeeklyQuest

personal_analysis_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔮 Тайна твоего предназначения',
                callback_data='destiny_mystery',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🚀 Карьера и финансы',
                callback_data='career_and_finance',
            ),
        ],
        [
            InlineKeyboardButton(
                text='❤ Твой код любви',
                callback_data='love_code',
            ),
        ],
        [
            InlineKeyboardButton(
                text='⚡ Твоя суперсила',
                callback_data='superpower',
            ),
        ],
        [
            InlineKeyboardButton(
                text='✨ Твой полный профиль',
                callback_data='full_profile',
            ),
        ],
    ],
)

start_ways_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✨ Погрузи меня сразу',
                callback_data='start_way_right_now',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🔎 Объясни, как это работает',
                callback_data='start_way_explain',
            ),
        ],
    ],
)

birth_times_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Утро (06:00–10:59)',
                callback_data='birth_time_08:00',
            ),
            InlineKeyboardButton(
                text='День (11:00–15:59)',
                callback_data='birth_time_13:00',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Вечер (16:00–20:59)',
                callback_data='birth_time_18:00',
            ),
            InlineKeyboardButton(
                text='Ночь (21:00–01:59)',
                callback_data='birth_time_23:00',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Раннее утро (02:00–05:59)',
                callback_data='birth_time_04:00',
            ),
            InlineKeyboardButton(
                text='Вообще не знаю',
                callback_data='birth_time_12:00',
            ),
        ],
    ],
)

notifications_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🔔 Да, получать послания',
                callback_data='notifications:yes',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🙂 Пока нет',
                callback_data='notifications:no',
            ),
        ],
    ],
)

back_to_personal_analysis_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='to_personal_analysis',
            ),
        ],
    ],
)

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

universe_advice_extended_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🌟 Открыть совет',
                callback_data='university_advice',
            ),
        ],
        [
            InlineKeyboardButton(
                text='📆 Узнать свой день',
                callback_data='personal_day',
            ),
        ],
    ],
)

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

month_with_soul_muse_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🎁 Персональный прогноз на месяц',
                callback_data='month_forecast',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🎁 Главный ресурс месяца',
                callback_data='month_main_resource',
            ),
        ],
        [
            InlineKeyboardButton(
                text='🎁 Твой сценарий месяца',
                callback_data='month_script',
            ),
        ],
    ],
)

premium_space_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🚀 Твой День силы',
                callback_data='power_day',
            ),
        ],
        [
            InlineKeyboardButton(
                text='✨ Ответ Вселенной',
                callback_data='universe_answer',
            ),
        ],
        [
            InlineKeyboardButton(
                text='VIP-совет от Soul Muse',
                callback_data='soul_muse_vip_answer',
            ),
        ],
    ],
)

vip_compatibility_payment_choices_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='2500 баллов', callback_data='astropoints'
            )
        ],
        [InlineKeyboardButton(text='1599 ₽', callback_data='money')],
    ]
)

connection_types_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='💞 Пара (романтическая)',
                callback_data='connection_type:couple',
            ),
            InlineKeyboardButton(
                text='🏡 Семья', callback_data='connection_type:family'
            ),
        ],
        [
            InlineKeyboardButton(
                text='🤝 Друзья', callback_data='connection_type:friends'
            ),
            InlineKeyboardButton(
                text='🚀 Команда / бизнес / коллеги',
                callback_data='connection_type:team',
            ),
        ],
    ]
)


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


def get_soul_muse_question_kb(
    *,
    ask_question_btn: bool = True,
    buy_extra_questions_btn: bool = True,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if ask_question_btn:
        kb.button(
            text='✍🏽 Задать вопрос Soul Muse',
            callback_data='ask_soul_muse',
        )
    if buy_extra_questions_btn:
        kb.button(
            text='💎 Купить дополнительные вопросы',
            callback_data='buy_more_soul_muse',
        )
    return kb.adjust(1).as_markup()


async def get_weekly_quest_kb(quest: WeeklyQuest):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Участвовать',
                    callback_data=f'participate_in_weekly_quest:{quest.pk}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='to_weekly_quests_list',
                ),
            ],
        ],
    )


def keyboard_from_choices(choices: type[Choices]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in choices.choices:
        kb.button(text=label, callback_data=value)
    return kb.adjust(1).as_markup()


def get_quest_statuses_kb(
    quest_type: Literal['daily', 'weekly'],
    quest_id: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in QuestStatuses.choices:
        kb.button(
            text=label,
            callback_data=f'quest:{quest_type}:{quest_id}:{value}',
        )
    return kb.adjust(1).as_markup()


def get_vip_compatability_report_kb(
    add_person_btn: bool,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if add_person_btn:
        kb.button(text='Добавить человека', callback_data='add_person')
    kb.button(text='Получить отчет', callback_data='vip_compatability_report')
    return kb.adjust(1).as_markup()
