from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from core.models import Client


class IsExpert(BaseFilter):
    async def __call__(
        self,
        msg: Message | CallbackQuery,
    ) -> bool | dict[str, Any]:
        pk = (
            msg.chat.id
            if isinstance(msg, Message)
            else msg.message.chat.id
        )
        client = await Client.objects.aget(pk=pk)
        return client.expert_type != ''
