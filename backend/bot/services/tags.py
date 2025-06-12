from bot.services.numerology import (
    get_fate_number,
    get_karmic_number,
    get_personality_number,
    get_soul_number,
)
from core.models import Client


def get_astrology_tags(client: Client) -> set[str]:
    tags = set()

    planets = {p['name']: p for p in client.planets}
    houses = client.houses
    aspects = client.aspects

    # 1. ЭМОЦИИ и ЧУВСТВОВАНИЕ
    moon = planets['Moon']
    moon_sign = moon['sign']
    moon_house = moon['house']

    if moon_sign in ['Capricorn', 'Virgo', 'Scorpio', 'Aquarius']:
        tags.add('эмоциональный интеллект')
    if moon_house == 12:
        tags.add('эмоциональный интеллект')
    if planets['Sun']['house'] == 12:
        tags.add('проявленность')
    if planets['Mercury']['sign'] == 'Pisces':
        tags.add('ясность')

    # 2. ГРАНИЦЫ и УВЕРЕННОСТЬ
    ascendant_sign = houses[0]['sign']
    venus = planets['Venus']
    north_node = planets['Node']

    if ascendant_sign == 'Libra':
        tags.add('границы')
    if venus['sign'] == 'Pisces':
        tags.add('границы')
    if north_node['sign'] == 'Aries':
        tags.add('уверенность')
    if venus['sign'] == 'Libra':
        tags.add('честность')
    if planets['Sun']['house'] == 7:
        tags.add('самоценность')

    # 3. САМООЦЕННОСТЬ и ВНУТРЕННЯЯ СИЛА
    if north_node['sign'] == 'Virgo':
        tags.add('уверенность')
    if venus['sign'] == 'Virgo':
        tags.add('самоценность')
    if planets['Mars']['sign'] == 'Cancer':
        tags.add('границы')
    if planets['Sun']['house'] == 6:
        tags.add('самоценность')

    # 4. ДОВЕРИЕ и ИНТУИЦИЯ
    if north_node['sign'] == 'Pisces':
        tags.add('интуиция')

    if ascendant_sign == 'Pisces':
        tags.add('самоидентичность')

    if planets['Mercury']['is_retro'] == 'true':
        tags.add('уверенность')

    # 5. ДИСЦИПЛИНА и РЕАЛИЗАЦИЯ
    if planets['Mars']['sign'] == 'Libra':
        tags.add('уверенность')

    if planets['Saturn']['house'] == 10:
        tags.add('ответственность')

    if planets['Jupiter']['house'] == 6:
        tags.add('власть')

    if north_node['sign'] == 'Capricorn':
        tags.add('власть')

    # 6. ТЕЛО и ЭНЕРГИЯ
    if planets['Mars']['sign'] == 'Taurus':
        tags.add('энергия')

    # АСПЕКТЫ
    for aspect in aspects:
        if (
            aspect['aspecting_planet'] == 'Moon'
            and aspect['aspected_planet'] == 'Pluto'
            and aspect['type'] == 'Square'
        ):
            tags.add('эмоциональный интеллект')

        if (
            aspect['aspecting_planet'] == 'Sun'
            and aspect['aspected_planet'] == 'Saturn'
            and aspect['type'] == 'Square'
        ):
            tags.add('самоценность')

        if (
            aspect['aspecting_planet'] == 'Mercury'
            and aspect['aspected_planet'] == 'Saturn'
            and aspect['type'] == 'Square'
        ):
            tags.add('проявленность')

        if (
            aspect['aspecting_planet'] == 'Sun'
            and aspect['aspected_planet'] == 'Neptune'
            and aspect['type'] == 'Opposition'
        ):
            tags.add('центрированность')

        if (
            aspect['aspecting_planet'] == 'Venus'
            and aspect['aspected_planet'] == 'Neptune'
            and aspect['type'] == 'Conjunction'
        ):
            tags.add('телесность')

    return tags


def get_hd_tags(client: Client) -> set[str]:
    tags = set()

    if client.type == 'Manifestor':
        tags.add('уверенность')
    elif client.type == 'Generator':
        tags.add('границы')
    elif client.type == 'Manifesting Generator':
        tags.add('фокус')
    elif client.type == 'Projector':
        tags.add('самоценность')
    elif client.type == 'Reflector':
        tags.add('самоидентичность')

    if client.authority == 'Emotional':
        tags.add('эмоциональный интеллект')
    elif client.authority == 'Sacral':
        tags.add('интуиция')
    elif client.authority == 'Mental':
        tags.add('ясность')

    if 'G' in client.centers:
        tags.add('самоидентичность')
    if 'Ego' in client.centers:
        tags.add('самоценность')
    if 'Solar Plexus' in client.centers:
        tags.add('эмоциональный интеллект')
    if 'Sacral' in client.centers:
        tags.add('энергия')
    if 'Ajna' in client.centers:
        tags.add('уверенность')
    if 'Throat' in client.centers:
        tags.add('проявленность')
    if 'Root' in client.centers:
        tags.add('спокойствие')
    if 'Spleen' in client.centers:
        tags.add('уверенность')
    if 'Head' in client.centers:
        tags.add('ясность')

    return tags


def get_numerology_tags(client: Client) -> set[str]:
    fate_number = get_fate_number(client.fullname, (11, 22, 33))
    karmic_number = get_karmic_number(client.fullname)
    soul_number = get_soul_number(client.fullname)
    personality_number = get_personality_number(client.fullname)
    tags_mapping = {
        'destiny': {
            1: {'уверенность'},
            2: {'границы'},
            3: {'фокус'},
            4: {'гибкость'},
            5: {'власть'},
            6: {'границы'},
            7: {'эмоциональный интеллект'},
            8: {'самоценность'},
            9: {'самоценность'},
            11: {'центрированность'},
            22: {'власть'},
            33: {'самоценность'},
        },
        'karmic': {
            1: {'уверенность'},
            2: {'партнёрство'},
            3: {'выражение'},
            4: {'власть'},
            5: {'гибкость'},
            6: {'зрелость'},
            7: {'интуиция'},
            8: {'власть'},
            9: {'отпускание'},
        },
        'soul': {
            2: {'самоценность'},
            6: {'границы'},
            7: {'открытость'},
        },
        'personality': {
            3: {'эмоциональный интеллект'},
            4: {'проявленность'},
            5: {'осознанность'},
        },
    }

    tags = set()
    if destiny_tags := tags_mapping['destiny'].get(fate_number):
        tags.update(destiny_tags)
    if karmic_tags := tags_mapping['karmic'].get(karmic_number):
        tags.update(karmic_tags)
    if soul_tags := tags_mapping['soul'].get(soul_number):
        tags.update(soul_tags)
    if personality_tags := tags_mapping['personality'].get(personality_number):
        tags.update(personality_tags)
    return tags


def get_archetype_tags(client: Client):
    archetype_tags = {
        1: 'уязвимость',
        2: 'границы',
        3: 'эмоциональный интеллект',
        4: 'завершение',
        5: 'центрированность',
        6: 'самоидентичность',
        7: 'эмоциональный интеллект',
        8: 'уверенность',
        9: 'практичность',
        11: 'связь',
        22: 'действие',
    }
    soul_number = get_soul_number(client.fullname)
    return {archetype_tags[soul_number]}


def get_client_tags(client: Client) -> set:
    return {
        *get_astrology_tags(client),
        *get_hd_tags(client),
        *get_numerology_tags(client),
        *get_archetype_tags(client),
    }
