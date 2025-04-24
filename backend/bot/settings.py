from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import Env

env = Env()
env.read_env()


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    HD_API_KEY: str = field(default_factory=lambda: env('HD_API_KEY'))
    HD_GEOCODE_KEY: str = field(default_factory=lambda: env('HD_GEOCODE_KEY'))
    ASTROLOGY_USER_ID: str = field(
        default_factory=lambda: env('ASTROLOGY_USER_ID'),
    )
    ASTROLOGY_API_KEY: str = field(
        default_factory=lambda: env('ASTROLOGY_API_KEY'),
    )
    OPENAI_API_KEY: str = field(default_factory=lambda: env('OPENAI_API_KEY'))

    CURRENCY: str = field(default='RUB')
    BOT_LINK: str = field(default='https://t.me/search_net_bot')
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')


settings = Settings()
