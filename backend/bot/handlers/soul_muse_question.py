from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.inline import (
    get_soul_muse_question_kb,
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from core.models import Actions, Client, SubscriptionPlans

router = Router()


@router.message(F.text == '🤖 Спроси у Soul Muse')
async def soul_muse_question(msg: Message):
    client: Client = await Client.objects.aget(pk=msg.chat.id)

    if not client.is_registered():
        await msg.answer(
            '🤖 Спроси у Soul Muse\n'
            'У тебя есть вопрос.\n'
            'Но я не могу услышать, пока ты не представился(ась).\n\n'
            'Пройди регистрацию — и тогда я отвечу. Не из ума. Из глубины.',
            reply_markup=get_to_registration_kb(
                text='🔓 Разблокировать доступ к вопросу',
            ),
        )
        return

    if client.has_action_permission(Actions.SOUL_MUSE_QUESTION):
        if client.subscription_plan == SubscriptionPlans.PREMIUM:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'У тебя есть пространство для настоящих вопросов.\n'
                'Пятнадцать шагов к себе — через ответы.\n\n'
                'Когда почувствуешь — просто задай. А я скажу, что ты давно знал(а), но боялся(ась) услышать.',
                reply_markup=get_soul_muse_question_kb(),
            )
        elif client.subscription_plan == SubscriptionPlans.STANDARD:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Иногда один вопрос — открывает целый пласт.\n'
                'Ты можешь задать до 4 вопросов. А потом — расширить доступ.\n\n'
                'Готов(а)? Я отвечаю из тишины. Но попадаю в самое точное.',
                reply_markup=get_soul_muse_question_kb(),
            )
        else:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Ты носишь в себе вопрос?\n'
                'О себе. О чувствах. О пути.\n'
                'Задай — и я отвечу. Точно, глубоко, без шаблонов.\n\n'
                'У тебя есть 2 вопроса. Используй их осознанно.',
                reply_markup=get_soul_muse_question_kb(),
            )
        return

    if client.action_limit_exceed(Actions.SOUL_MUSE_QUESTION):
        if client.subscription_is_active():
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Ты уже использовал(а) все включённые вопросы.\n\n'
                'Хочешь продолжить исследовать себя?\n\n'
                'Можешь докупить доступ и задать ещё.\n'
                'Я рядом.',
                reply_markup=get_soul_muse_question_kb(),
            )
        else:
            await msg.answer(
                '🤖 Спроси у Soul Muse\n'
                'Ты уже почувствовал(а), как звучит мой голос.\n'
                'Но сейчас я молчу — пока ты не вернёшься.\n\n'
                'Оформи доступ — и я снова услышу твой вопрос.',
                reply_markup=get_to_subscription_plans_kb(),
            )
