import json
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import Env

env = Env()
env.read_env()


@dataclass
class Media:
    privacy_policy: str = ''
    public_offer: str = ''
    soul_mind: str = ''
    soul_muse: str = ''
    soul_mind_video: str = ''
    soul_muse_video: str = ''

    @classmethod
    def from_file(cls):
        with open('media.json') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    MEDIA: Media = field(default_factory=lambda: Media.from_file())
    ADMINS: list = field(default_factory=lambda: [1736885484])

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
    TRIAL_WEEKLY_QUEST_ID: str = field(default=1)
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')
    PAGE_SIZE: int = field(default=5)

    PRIVACY_POLICY_URL: str = field(
        default=(
            'https://docs.google.com/document/d/'
            '11eEnAiY9y1IbVk9CtvyEzvIC0mLU6nxG/edit?usp=drive_link'
            '&ouid=111038030028092199179&rtpof=true&sd=true'
        )
    )
    PUBLIC_OFFER_URL: str = field(
        default=(
            'https://docs.google.com/document/d/'
            '1PRFVMc8NSMVvD8L37d7dZzNx5uxI7wp4/edit?usp=drive_link'
            '&ouid=111038030028092199179&rtpof=true&sd=true'
        )
    )


settings = Settings()
