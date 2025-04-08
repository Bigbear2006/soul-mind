from datetime import datetime
from typing import Any

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from core.models import Client


class SubscriptionFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool | dict[str, Any]:
        client = await Client.objects.aget(pk=msg.chat.id)

        if client.subscription_end and client.subscription_end > datetime.now(
            settings.TZ,
        ):
            return True

        if not client.subscription_plan:
            text = 'Оформить подписку'
        else:
            text = 'Продлить подписку'

        await msg.answer(
            f'Чтобы пользоваться этой функцией, вам нужно {text.lower()}',
            reply_markup=one_button_keyboard(
                text=text,
                callback_data='subscription_plans',
            ),
        )
        raise SkipHandler()
