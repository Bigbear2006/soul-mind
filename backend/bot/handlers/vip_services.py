from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import vip_services_kb
from bot.keyboards.utils import one_button_keyboard

router = Router()


@router.message(F.text == 'VIP-Услуги')
@router.callback_query(F.data == 'vip_services')
async def vip_services_handler(msg: Message | CallbackQuery):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    await answer_func(
        '💎 VIP-Услуги от Soul Muse\n\n'
        'У каждого — свой запрос.\n'
        'Иногда он требует большего пространства.\n'
        'Разбор только о тебе. Голос только для тебя.\n'
        'Глубже. Ближе.\n'
        'Выбирай, что откликается.',
        reply_markup=vip_services_kb,
    )


@router.callback_query(F.data == 'vip_mini_consult')
async def vip_mini_consult(callback: CallbackQuery):
    await callback.message.edit_text(
        '🎧 Мини-консультация с экспертом\n\n'
        'У тебя есть вопрос, и он требует живого голоса.\n'
        'Астролог. Нумеролог. Эксперт по Хьюман-дизайну. '
        'Психолог. Духовный наставник-энергопрактик.\n\n'
        '3–5 голосовых от того, кто умеет читать глубже.',
        reply_markup=one_button_keyboard(
            text='✨ Задать вопрос эксперту – 999 ₽ / 1500 баллов',
            callback_data='buy_mini_consult',
            back_button_data='vip_services',
        ),
    )


@router.callback_query(F.data == 'vip_personal_report')
async def vip_personal_report(callback: CallbackQuery):
    await callback.message.edit_text(
        '📄 Глубокий персональный отчёт\n\n'
        'Ты хочешь не просто вдохновение — ты хочешь ориентиры.\n'
        'Этот отчёт — как карта с метками: где ты сейчас, куда направлена твоя энергия,\n'
        'и что важно не пропустить в этом месяце.\n\n'
        'PDF + голос Soul Muse.\n'
        'Без гаданий. С точкой фокуса.',
        reply_markup=one_button_keyboard(
            text='🌀 Получить отчёт – 1299 ₽ / 2000 баллов',
            callback_data='buy_personal_report',
            back_button_data='vip_services',
        ),
    )


@router.callback_query(F.data == 'vip_compatibility')
async def vip_compatibility(callback: CallbackQuery):
    await callback.message.edit_text(
        '❤️‍🔥 VIP-анализ совместимости\n\n'
        'Ты готов(а) к настоящей глубине?\n'
        'Это больше, чем просто “подходите вы друг другу или нет”.\n'
        'Это разбор, после которого вы оба увидите себя иначе.\n\n'
        'Пара. Семья. Команда. Друзья.\n'
        'Выбирай формат — и ныряем вглубь.',
        reply_markup=one_button_keyboard(
            text='💎 Узнать глубину связи – 1599 ₽ / 2500 баллов',
            callback_data='buy_compatibility',
            back_button_data='vip_services',
        ),
    )
