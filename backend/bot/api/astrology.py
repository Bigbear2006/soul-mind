import datetime
from dataclasses import asdict

from aiohttp import BasicAuth, ClientSession

from bot.loader import logger
from bot.schemas import AstrologyParams, House, Planet, WesternHoroscope
from bot.settings import settings


class AstrologyAPI:
    def __init__(self, **session_kwargs):
        self.session = ClientSession(
            'https://json.astrologyapi.com/v1/',
            headers=self.headers,
            auth=self.auth,
            **session_kwargs,
        )

    @property
    def headers(self):
        return {
            'Accept-Language': 'en',
        }

    @property
    def auth(self):
        return BasicAuth(
            settings.ASTROLOGY_USER_ID,
            settings.ASTROLOGY_API_KEY,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @staticmethod
    def degree_to_gate(norm_degree) -> int:
        return int(norm_degree // 5.2) + 1

    @staticmethod
    def get_transit_gates(planets: list[Planet]) -> dict[str, int]:
        return {
            p.name: AstrologyAPI.degree_to_gate(p.norm_degree) for p in planets
        }

    async def western_horoscope(
        self,
        data: AstrologyParams,
    ) -> WesternHoroscope:
        async with self.session.post(
            'western_horoscope',
            json=asdict(data),
        ) as rsp:
            data = await rsp.json()
            logger.info(data)
        return WesternHoroscope(
            planets=[Planet(**i) for i in data['planets']],
            houses=[House(**i) for i in data['houses']],
        )

    async def get_timezone(
        self,
        latitude: float,
        longitude: float,
        date: datetime.date,
    ) -> float:
        async with self.session.post(
            'timezone_with_dst',
            json={
                'latitude': latitude,
                'longitude': longitude,
                'date': date.strftime('%m-%d-%Y'),
            },
        ) as rsp:
            data = await rsp.json()
            logger.info(data)
        return float(data['timezone'])


# from bot.api.astrology import AstrologyAPI
# from bot.schemas import AstrologyParams
# async with AstrologyAPI() as api:
#     p = AstrologyParams(**{
#       'day': 6,
#       'month': 1,
#       'year': 2000,
#       'hour': 7,
#       'min': 45,
#       'lat': 19.132,
#       'lon': 72.342,
#       'tzone': 5.5,
#     })
#     print(await api.western_horoscope(p))
