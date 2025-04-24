from collections.abc import Sequence, Callable
from datetime import date

from bot.templates.base import pythagorean_matrix


def calculate_number(number: int | str, master_numbers: Sequence[int]) -> int:
    if isinstance(number, int) or number.isdigit():
        number = int(number)
        if number <= 9 or number in master_numbers:
            return number

    number = sum([int(i) for i in str(number) if i.isdigit()])
    return calculate_number(number, master_numbers)


def get_life_path_number(birth_date: date) -> int:
    return calculate_number(str(birth_date), (11, 22, 33))


def reduce_number(number: int) -> int:
    return calculate_number(number, ())


def fullname_to_number(fullname: str, condition: Callable[[str], bool]) -> int:
    number = sum(
        [
            pythagorean_matrix[i]
            for i in fullname.strip().upper()
            if condition(i)
        ]
    )
    return calculate_number(number, (11, 22))


def get_soul_number(fullname: str) -> int:
    return fullname_to_number(fullname, lambda x: x in 'АЕЁИОУЫЭЮЯ')


def get_personality_number(fullname: str) -> int:
    return fullname_to_number(fullname, lambda x: x not in 'АЕЁИОУЫЭЮЯ')


def get_fate_number(fullname: str) -> int:
    return fullname_to_number(fullname, lambda x: x)
