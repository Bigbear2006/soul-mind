from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.inline import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from core.models import Actions, Client

router = Router()


@router.message(F.text == '💞 Энергия вашей совместимости')
async def compatability_energy(msg: Message):
    client: Client = await Client.objects.aget(pk=msg.chat.id)

    if not client.is_registered():
        await msg.answer(
            'Ты хочешь понять вас,\n'
            'но ещё не заглянул(а) в себя?\n\n'
            'Пройди регистрацию — и я покажу, как сплетается ваша энергия.',
            reply_markup=get_to_registration_kb(),
        )
        return

    if client.action_limit_exceed(Actions.COMPATABILITY_ENERGY):
        await msg.answer(
            'Твоя энергия не ограничена тремя людьми.\n'
            'Каждая новая связь — это отражение тебя.\n\n'
            'Разблокируй ещё совместимости\n\n'
            '🔹 1 совместимость → 159 ₽ или 250 астробаллов\n'
            '🔹 3 совместимости → 399 ₽ или 650 астробаллов\n'
            '🔹 VIP-анализ совместимости\n\n'
            'Ты готов(а) к настоящей глубине?\n'
            'Это больше, чем просто “подходите вы друг другу или нет”.\n'
            'Это разбор, после которого вы оба увидите себя иначе.\n\n'
            'Пара. Семья. Команда. Друзья.\n'
            'Выбирай формат — и ныряем вглубь.\n\n'
            '💎 Получить индивидуальный разбор\n'
            'Стоимость —> 1599 ₽ или 2500 астробаллов',
        )
        return

    if client.has_action_permission(Actions.COMPATABILITY_ENERGY):
        await msg.answer(
            'Случайных встреч не бывает.\n'
            'Я покажу, почему этот человек рядом — и чему вы учите друг друга.\n\n'
            'Ты готов(а) взглянуть на вашу связь по-настоящему?',
        )
    else:
        await msg.answer(
            'Связь, которую ты хочешь понять,\n'
            'не раскрывается за пару строк.\n\n'
            'Продолжи путь — и я покажу, что между вами на самом деле.',
            reply_markup=get_to_subscription_plans_kb(),
        )


# TODO: Премиум-подписка - Подпись под результатом (как контекстное предложение)
