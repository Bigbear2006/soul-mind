from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import Env

env = Env()
env.read_env()


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))
    OPENAI_API_KEY: str = field(default_factory=lambda: env('OPENAI_API_KEY'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))

    BOT_LINK: str = field(default='https://t.me/learnpoemsbot')
    CURRENCY: str = field(default='RUB')
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')


settings = Settings()
