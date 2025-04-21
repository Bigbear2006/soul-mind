from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.inline import get_to_registration_kb, personal_analysis_kb
from core.models import Client


def get_personal_analysis_intro(
    client: Client,
) -> tuple[str, InlineKeyboardMarkup]:
    if not client.is_registered():
        return (
            'Ты хочешь узнать, кто ты на самом деле — '
            'но ещё даже не сделал первый шаг?\n\n'
            'Зарегистрируйся. Без этого я не смогу рассказать тебе '
            'самую важную историю — твою.',
            get_to_registration_kb(
                back_button_data='to_personal_analysis',
            ),
        )
    else:
        return (
            'Это не просто разбор.\n'
            'Это откровение.\n'
            'Ты — гораздо глубже, чем думаешь.\n'
            'Позволь себе вспомнить, кем ты был до того, '
            'как мир сказал тебе, кем должен быть.',
            personal_analysis_kb,
        )
