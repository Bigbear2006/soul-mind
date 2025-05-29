from typing import Any

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from django.core.exceptions import ObjectDoesNotExist

from core.models import Client, ClientExpertType


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
            expert_types = (
                await ClientExpertType.objects.filter(client=client).acount()
            )
            if expert_types == 0:
                raise SkipHandler
        except ObjectDoesNotExist:
            raise SkipHandler

        return True
