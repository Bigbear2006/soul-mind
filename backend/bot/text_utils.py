import re

from core.choices import Genders


def plural(n: int, forms: tuple[str, str, str]) -> str:
    n = abs(n) % 100
    n1 = n % 10
    if 10 < n < 20:
        return forms[2]
    if 1 < n1 < 5:
        return forms[1]
    if n1 == 1:
        return forms[0]
    return forms[2]


def questions_plural(n: int):
    return plural(n, ('вопрос', 'вопроса', 'вопросов'))


def compatability_plural(n: int):
    return plural(n, ('совместимость', 'совместимости', 'совместимостей'))


def your_plural(sign: str):
    if sign == 'Virgo':
        return 'Твоя'
    if sign in ('Gemini', 'Libra', 'Pisces'):
        return 'Твои'
    return 'Твой'


def split_text(
    text: str,
    *,
    max_length: int = 250,
    sep: str = '.',
) -> list[str]:
    text_chunks = []
    for i in text.split(sep):
        if not text_chunks:
            text_chunks.append(i)
            continue
        if len(text_chunks[-1]) + len(sep) + (len(i)) < max_length:
            text_chunks[-1] = f'{text_chunks[-1]}{sep}{i}'
        else:
            text_chunks.append(i)
    return text_chunks


def genderize(text: str, *, gender: str, prefix: str = 'gender') -> str:
    def replace(match: re.Match[str]) -> str:
        male, female = match.group(1).split(',')
        return male if gender == Genders.MALE else female

    return re.sub(rf'{{{prefix}:([^}}]+)}}', replace, text)
