from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message

from core.models import Client


class IsExpert(BaseFilter):
    async def __call__(self, msg: Message, client: Client) -> bool | dict[str, Any]:
        return client.expert_type != ''
