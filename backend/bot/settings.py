import json
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import Env

env = Env()
env.read_env()


@dataclass
class Media:
    privacy_policy: str
    public_offer: str

    @classmethod
    def from_file(cls):
        with open('bot/media.json') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    MEDIA: Media = field(default_factory=lambda: Media.from_file())
    CAN_LOAD_MEDIA: list = field(default_factory=lambda: [1736885484])

    HD_API_KEY: str = field(default_factory=lambda: env('HD_API_KEY'))
    HD_GEOCODE_KEY: str = field(default_factory=lambda: env('HD_GEOCODE_KEY'))
    ASTROLOGY_USER_ID: str = field(
        default_factory=lambda: env('ASTROLOGY_USER_ID'),
    )
    ASTROLOGY_API_KEY: str = field(
        default_factory=lambda: env('ASTROLOGY_API_KEY'),
    )
    OPENAI_API_KEY: str = field(default_factory=lambda: env('OPENAI_API_KEY'))
    YANDEX_API_KEY: str = field(default_factory=lambda: env('YANDEX_API_KEY'))

    CURRENCY: str = field(default='RUB')
    BOT_LINK: str = field(default='https://t.me/search_net_bot')
    EXPERTS_CHAT_ID: int = field(default=-1002309981972)
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')


settings = Settings()
