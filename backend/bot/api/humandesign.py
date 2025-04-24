import json
from dataclasses import asdict

from aiohttp import ClientSession

from bot.schemas import HDInputData, HDOutputData
from bot.settings import settings


class HumanDesignAPI:
    def __init__(self, **session_kwargs):
        self.session = ClientSession(
            'https://api.humandesignapi.nl/v1/',
            **session_kwargs,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @staticmethod
    def get_headers():
        return {
            'Content-Type': 'application/json',
            'HD-Api-Key': settings.HD_API_KEY,
            'HD-Geocode-Key': settings.HD_GEOCODE_KEY,
        }

    async def bodygraphs(self, data: HDInputData) -> HDOutputData:
        async with self.session.post(
            'bodygraphs',
            headers=self.get_headers(),
            data=json.dumps(asdict(data)),
        ) as rsp:
            data = await rsp.json()
            print(json.dumps(data, indent=2))
            return HDOutputData(
                type=data['type'],
                profile=data['profile'],
                centers=data['centers'],
                strategy=data['strategy'],
                authority=data['authority'],
            )
