import datetime
from dataclasses import asdict

from aiohttp import BasicAuth

from bot.api.base import APIClient
from bot.loader import logger
from bot.schemas import (
    Aspect,
    HoroscopeParams,
    House,
    Planet,
    WesternHoroscope,
)
from bot.settings import settings


class AstrologyAPI(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://json.astrologyapi.com/v1/',
            headers=self.headers,
            auth=self.auth,
            **session_kwargs,
        )

    @property
    def headers(self):
        return {'Accept-Language': 'en'}

    @property
    def auth(self):
        return BasicAuth(
            settings.ASTROLOGY_USER_ID,
            settings.ASTROLOGY_API_KEY,
        )

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
        data: HoroscopeParams,
    ) -> WesternHoroscope:
        async with self.session.post(
            'western_horoscope',
            json=asdict(data),
        ) as rsp:
            data = await rsp.json()
            logger.debug(data) if data.get('planets') else logger.info(data)
        return WesternHoroscope(
            planets=[Planet(**i) for i in data['planets']],
            houses=[House(**i) for i in data['houses']],
            aspects=[Aspect(**i) for i in data['aspects']],
        )

    async def get_tropical_planets(self, data: HoroscopeParams):
        async with self.session.post(
            'planets/tropical',
            json=asdict(data),
        ) as rsp:
            data = await rsp.json()
        return [
            Planet(
                name=i['name'],
                full_degree=i['fullDegree'],
                norm_degree=i['normDegree'],
                speed=i['speed'],
                is_retro=i['is_retro'],
                sign=i['sign'],
                house=i['house'],
            )
            for i in data
        ]

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
            logger.debug(data) if data.get('timezone') else logger.info(data)
        return float(data['timezone'])
