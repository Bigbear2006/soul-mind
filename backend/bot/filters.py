from typing import Any

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from django.core.exceptions import ObjectDoesNotExist

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

        try:
            client = await Client.objects.aget(pk=pk)
            if client.expert_type == '':
                raise SkipHandler
        except ObjectDoesNotExist:
            raise SkipHandler

        return True
