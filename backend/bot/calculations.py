import re
from collections.abc import Callable, Sequence
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


def fullname_to_number(
    fullname: str,
    condition: Callable[[str], bool],
    master_numbers: Sequence[[int]] = None,
) -> int:
    if not master_numbers:
        master_numbers = (11, 22)
    number = sum(
        [
            pythagorean_matrix[i]
            for i in re.sub(r'[^а-яА-ЯёЁ]', '', fullname).upper()
            if condition(i)
        ],
    )
    return calculate_number(number, master_numbers)


def get_soul_number(fullname: str) -> int:
    return fullname_to_number(fullname, lambda x: x in 'АЕЁИОУЫЭЮЯ')


def get_personality_number(fullname: str) -> int:
    return fullname_to_number(fullname, lambda x: x not in 'АЕЁИОУЫЭЮЯ')


def get_fate_number(
    fullname: str,
    master_numbers: Sequence[int] = None,
) -> int:
    return fullname_to_number(fullname, lambda x: x, master_numbers)


def get_karmic_number(fullname: str) -> int | None:
    try:
        return list(
            set(range(1, 10))
            - {
                pythagorean_matrix[i]
                for i in re.sub(r'[^а-яА-ЯёЁ]', '', fullname).upper()
            },
        )[0]
    except IndexError:
        return None


def get_power_day(birth_date: date):
    return get_life_path_number(birth_date) + date.today().month
