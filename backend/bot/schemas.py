from dataclasses import dataclass
from datetime import datetime

from core.models import Client


@dataclass
class HDInputData:
    birthdate: str = '05-Sep-90'
    birthtime: str = '21:17'
    location: str = 'Amsterdam'


@dataclass
class HDOutputData:
    type: str
    profile: str
    centers: list[str]
    strategy: str
    authority: str


@dataclass
class AstrologyParams:
    day: int
    month: int
    year: int
    hour: int
    min: int
    lat: float
    lon: float
    tzone: float

    @classmethod
    def from_client(cls, client: Client):
        return cls(
            day=client.birth.day,
            month=client.birth.month,
            year=client.birth.year,
            hour=client.birth.hour,
            min=client.birth.min,
            lat=client.birth_latitude,
            lon=client.birth_longitude,
            tzone=3,
        )


@dataclass
class Planet:
    name: str
    full_degree: float
    norm_degree: float
    speed: float
    is_retro: bool
    sign_id: int
    sign: str
    house: int


@dataclass
class LunarMetric:
    month: str
    moon_sign: str
    moon_phase: str
