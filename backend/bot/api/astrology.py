from dataclasses import asdict

from Tools.scripts.generate_opcode_h import header
from aiohttp import ClientSession, BasicAuth

from bot.schemas import Planet, AstrologyParams, LunarMetric
from bot.settings import settings


class AstrologyAPI:
    def __init__(self, **session_kwargs):
        self.session = ClientSession(
            'https://json.astrologyapi.com/v1/',
            **session_kwargs,
        )

    @property
    def headers(self):
        return {
            'Accept-Language': 'ru',
        }

    @property
    def auth(self):
        return BasicAuth(
            settings.ASTROLOGY_USER_ID, settings.ASTROLOGY_API_KEY
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def western_horoscope(self, data: AstrologyParams) -> list[Planet]:
        async with self.session.post(
            'western_horoscope',
            json=asdict(data),
            auth=self.auth,
            headers=self.headers,
        ) as rsp:
            data = await rsp.json()
        return [Planet(**i) for i in data['planets']]

    async def get_moon_sign(self, data: AstrologyParams):
        planets = await self.western_horoscope(data)
        return [i for i in planets if i.name == 'Луна'][0]

    async def lunar_metrics(self, data: AstrologyParams) -> LunarMetric:
        async with self.session.post(
            'lunar_metrics',
            json=asdict(data),
            auth=self.auth,
        ) as rsp:
            data = await rsp.json()
            print(data)
        return LunarMetric(
            month=data['month'],
            moon_sign=data['moon_sign'],
            moon_phase=data['moon_phase'],
        )


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
#     print(await api.lunar_metrics(p))
