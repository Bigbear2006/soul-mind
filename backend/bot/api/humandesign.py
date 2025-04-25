import json
from dataclasses import asdict

from aiohttp import ClientSession

from bot.loader import logger
from bot.schemas import Bodygraphs, HDInputData
from bot.settings import settings


class HumanDesignAPI:
    def __init__(self, **session_kwargs):
        self.session = ClientSession(
            'https://api.humandesignapi.nl/v1/',
            headers=self.headers,
            **session_kwargs,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

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
            logger.info(data)
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
