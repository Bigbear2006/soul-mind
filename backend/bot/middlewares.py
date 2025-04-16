from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject

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
            if isinstance(event, Message):
                (
                    client,
                    created,
                ) = await Client.objects.create_or_update_from_tg_user(
                    event.from_user,
                )
                data['client'] = client
                data['client_created'] = created
            else:
                client = await Client.objects.aget(pk=event.message.chat.id)
                data['client'] = client
        return await handler(event, data)
