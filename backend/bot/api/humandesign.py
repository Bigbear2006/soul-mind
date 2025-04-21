import json
from dataclasses import asdict

from aiohttp import ClientSession

from bot.schemas import HDInputData
from bot.settings import settings


class HumanDesignAPI:
    def __init__(self, session: ClientSession):
        self.session = session

    @staticmethod
    def get_headers():
        return {
            'Content-Type': 'application/json',
            'HD-Api-Key': settings.HD_API_KEY,
            'HD-Geocode-Key': settings.HD_GEOCODE_KEY,
        }

    async def bodygraphs(self, data: HDInputData) -> dict:
        async with self.session.post(
            'https://api.humandesignapi.nl/v1/bodygraphs',
            headers=self.get_headers(),
            data=json.dumps(asdict(data)),
        ) as rsp:
            print(await rsp.text())
            return await rsp.json()
