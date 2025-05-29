from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject
from django.core.exceptions import ObjectDoesNotExist

from bot.loader import logger
from core.models import Client


class WithClientMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        with_client = get_flag(data, 'with_client')
        if with_client:
            pk = (
                event.chat.id
                if isinstance(event, Message)
                else event.message.chat.id
            )
            try:
                client = await Client.objects.aget(pk=pk)
                data['client'] = client
            except ObjectDoesNotExist:
                logger.info(event)
        return await handler(event, data)
