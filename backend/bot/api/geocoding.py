from bot.api.base import APIClient
from bot.loader import logger
from bot.settings import settings


class GeocodingAPI(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://maps.googleapis.com/maps/api/',
            **session_kwargs,
        )

    async def get_coordinates(self, address: str) -> tuple[float, float]:
        async with self.session.get(
            'geocode/json',
            params={'address': address, 'key': settings.HD_GEOCODE_KEY},
        ) as rsp:
            data = await rsp.json()
            logger.debug(data)
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
