from dataclasses import dataclass


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
