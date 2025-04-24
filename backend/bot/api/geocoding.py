from aiohttp import ClientSession

from bot.loader import logger
from bot.settings import settings


# 47.2357137, 39.701505
class GeocodingAPI:
    def __init__(self, **session_kwargs):
        self.session = ClientSession(
            'https://maps.googleapis.com/maps/api/',
            **session_kwargs,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_coordinates(self, address: str) -> tuple[float, float]:
        async with self.session.get(
            'geocode/json',
            params={'address': address, 'key': settings.HD_GEOCODE_KEY},
        ) as rsp:
            data = await rsp.json()
            logger.info(data)
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
