from datetime import datetime

from aiogram import F, Router, flags
from aiogram.types import Message

from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from core.models import Client, SubscriptionPlanChoices

router = Router()


@router.message(F.text == '👤 Личный кабинет')
@flags.with_client
async def personal_account_handler(msg: Message, client: Client):
    text = f'Астробаллы: {client.astropoints}\n'

    if client.subscription_end:
        sub_plan = SubscriptionPlanChoices(client.subscription_plan)
        sub_end = datetime.strftime(
            client.subscription_end.astimezone(settings.TZ),
            settings.DATE_FMT,
        )
        text += (
            f'Подписка: {sub_plan.label}\nДата окончания подписки {sub_end}'
        )
        button_text = 'Продлить подписку'
    else:
        text += 'Вы еще не оформляли подписку'
        button_text = 'Оформить подписку'

    await msg.answer(
        text,
        reply_markup=one_button_keyboard(
            text=button_text,
            callback_data='subscription_plans',
        ),
    )
