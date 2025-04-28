from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


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
            callback_data='buy_more_questions',
        )
    return kb.adjust(1).as_markup()


buy_questions_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='1 персональный вопрос',
                callback_data='buy_question:one',
            ),
        ],
        [
            InlineKeyboardButton(
                text='5 персональных вопросов',
                callback_data='buy_question:five',
            ),
        ],
    ],
)
