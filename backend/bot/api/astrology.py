import datetime
from dataclasses import asdict

from aiohttp import BasicAuth, ClientSession

from bot.loader import logger
from bot.schemas import AstrologyParams, Planet, House
from bot.settings import settings
from core.models import Client

PLANETS = {
    'planets': [
        {
            'name': 'Sun',
            'full_degree': 275.6427,
            'norm_degree': 5.6427,
            'speed': 1.019,
            'is_retro': 'false',
            'sign_id': 10,
            'sign': 'Capricorn',
            'house': 2,
        },
        {
            'name': 'Moon',
            'full_degree': 12.271,
            'norm_degree': 12.271,
            'speed': 13.5085,
            'is_retro': 'false',
            'sign_id': 1,
            'sign': 'Aries',
            'house': 5,
        },
        {
            'name': 'Mars',
            'full_degree': 232.2381,
            'norm_degree': 22.2381,
            'speed': 0.6621,
            'is_retro': 'false',
            'sign_id': 8,
            'sign': 'Scorpio',
            'house': 12,
        },
        {
            'name': 'Mercury',
            'full_degree': 278.3033,
            'norm_degree': 8.3033,
            'speed': 1.6049,
            'is_retro': 'false',
            'sign_id': 10,
            'sign': 'Capricorn',
            'house': 2,
        },
        {
            'name': 'Jupiter',
            'full_degree': 20.033,
            'norm_degree': 20.033,
            'speed': 0.043,
            'is_retro': 'false',
            'sign_id': 1,
            'sign': 'Aries',
            'house': 5,
        },
        {
            'name': 'Venus',
            'full_degree': 307.0102,
            'norm_degree': 7.0102,
            'speed': 1.2339,
            'is_retro': 'false',
            'sign_id': 11,
            'sign': 'Aquarius',
            'house': 3,
        },
        {
            'name': 'Saturn',
            'full_degree': 264.9924,
            'norm_degree': 24.9924,
            'speed': 0.117,
            'is_retro': 'false',
            'sign_id': 9,
            'sign': 'Sagittarius',
            'house': 1,
        },
        {
            'name': 'Uranus',
            'full_degree': 267.4199,
            'norm_degree': 27.4199,
            'speed': 0.0601,
            'is_retro': 'false',
            'sign_id': 9,
            'sign': 'Sagittarius',
            'house': 1,
        },
        {
            'name': 'Neptune',
            'full_degree': 277.6325,
            'norm_degree': 7.6325,
            'speed': 0.0379,
            'is_retro': 'false',
            'sign_id': 10,
            'sign': 'Capricorn',
            'house': 2,
        },
        {
            'name': 'Pluto',
            'full_degree': 221.8913,
            'norm_degree': 11.8913,
            'speed': 0.0273,
            'is_retro': 'false',
            'sign_id': 8,
            'sign': 'Scorpio',
            'house': 12,
        },
        {
            'name': 'Node',
            'full_degree': 357.3824,
            'norm_degree': 27.3824,
            'speed': -0.053,
            'is_retro': 'true',
            'sign_id': 12,
            'sign': 'Pisces',
            'house': 4,
        },
        {
            'name': 'Chiron',
            'full_degree': 85.3981,
            'norm_degree': 25.3981,
            'speed': -0.0619,
            'is_retro': 'true',
            'sign_id': 3,
            'sign': 'Gemini',
            'house': 7,
        },
        {
            'name': 'Part of Fortune',
            'full_degree': 144.086,
            'norm_degree': 24.086,
            'speed': 0,
            'is_retro': 'false',
            'sign_id': 5,
            'sign': 'Leo',
            'house': 9,
        },
    ],
}


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

    async def western_horoscope(self, data: AstrologyParams) -> tuple[list[Planet], list[House]]:
        async with self.session.post(
            'western_horoscope',
            json=asdict(data),
        ) as rsp:
            data = await rsp.json()
            # data = PLANETS
            logger.info(data)
        return [Planet(**i) for i in data['planets']], [House(**i) for i in data['houses']]

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
            # data = {'timezone': 3}
            logger.info(data)
        return float(data['timezone'])


async def western_horoscope(client: Client) -> list[Planet]:
    async with AstrologyAPI() as api:
        planets = await api.western_horoscope(
            AstrologyParams.from_client(client),
        )
    return planets


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
