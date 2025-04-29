import json
from dataclasses import asdict

from bot.api.base import APIClient
from bot.loader import logger
from bot.schemas import Bodygraphs, HDInputData
from bot.settings import settings


class HumanDesignAPI(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://api.humandesignapi.nl/v1/',
            headers=self.headers,
            **session_kwargs,
        )

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json',
            'HD-Api-Key': settings.HD_API_KEY,
            'HD-Geocode-Key': settings.HD_GEOCODE_KEY,
        }

    async def bodygraphs(self, data: HDInputData) -> Bodygraphs:
        async with self.session.post(
            'bodygraphs',
            data=json.dumps(asdict(data)),
        ) as rsp:
            data = await rsp.json()
            logger.debug(data)
            return Bodygraphs(
                type=data['type'],
                profile=data['profile'],
                centers=data['centers'],
                strategy=data['strategy'],
                authority=data['authority'],
                gates=data['gates'],
                definition=data['definition'],
                channels_long=data['channels_long'],
            )
