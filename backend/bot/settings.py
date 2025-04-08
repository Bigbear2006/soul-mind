from dataclasses import dataclass, field

from environs import Env

env = Env()
env.read_env()


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))
    OPENAI_API_KEY: str = field(default_factory=lambda: env('OPENAI_API_KEY'))
    BOT_LINK: str = field(default='https://t.me/search_net_bot')


settings = Settings()
