from bot.api.base import APIClient
from bot.loader import logger


class TelegraphyxAPI(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://app.telegraphyx.ru/api/bot/',
            **session_kwargs,
        )

    async def send_start_param(self, start_param: str):
        async with self.session.get(
            'start',
            params={'start': start_param},
        ) as rsp:
            data = await rsp.json()
            logger.info(data)


async def send_start_param(start_param: str):
    async with TelegraphyxAPI() as api:
        await api.send_start_param(start_param)
