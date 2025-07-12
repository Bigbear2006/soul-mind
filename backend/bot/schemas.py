from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from core.models import Client


# human design
@dataclass
class HDInputData:
    birthdate: str
    birthtime: str
    location: str

    @classmethod
    def from_datetime(cls, birth: datetime, location: str):
        return cls(
            birthdate=birth.strftime('%m.%d.%Y'),
            birthtime=birth.strftime('%H:%M'),
            location=location,
        )


@dataclass
class Bodygraphs:
    type: str
    profile: str
    centers: list[str]
    strategy: str
    authority: str
    gates: list[str]
    definition: str
    channels_long: list[str]

    @classmethod
    def from_client(cls, client: Client):
        return cls(
            type=client.type,
            profile=client.profile,
            centers=client.centers,
            strategy=client.strategy,
            authority=client.authority,
            gates=client.gates,
            definition=client.definition,
            channels_long=client.channels_long,
        )


# astrology
@dataclass
class HoroscopeParams:
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
            min=client.birth.minute,
            lat=client.birth_latitude,
            lon=client.birth_longitude,
            tzone=client.tzone,
        )


@dataclass
class Planet:
    name: str
    full_degree: float
    norm_degree: float
    speed: float
    is_retro: bool
    sign: str
    house: int
    sign_id: int | None = None


@dataclass
class House:
    house: int
    sign: str
    degree: float
    sign_id: int | None = None


@dataclass
class Aspect:
    aspecting_planet: str
    aspected_planet: str
    aspecting_planet_id: int
    aspected_planet_id: int
    aspect_type: int
    type: str
    orb: float
    diff: float


@dataclass
class WesternHoroscope:
    planets: list[Planet]
    houses: list[House]
    aspects: list[Aspect]


# yookassa
@dataclass(frozen=True)
class Payment:
    id: str
    confirmation_url: str


class PaymentStatus(StrEnum):
    """https://yookassa.ru/developers/payment-acceptance/getting-started/payment-process#lifecycle"""

    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'
