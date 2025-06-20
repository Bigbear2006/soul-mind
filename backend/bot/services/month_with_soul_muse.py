import random
from datetime import date, datetime, timedelta

from django.utils.timezone import now

from bot.api.astrology import AstrologyAPI
from bot.schemas import HoroscopeParams, Planet
from bot.services.numerology import get_month_number, get_soul_number
from bot.text_templates.base import aspect_angles
from bot.text_templates.month_with_soul_muse import (
    aspect_fallback_texts,
    balance_tips_descriptions,
    hd_gates_descriptions,
    month_archetypes_descriptions,
    moon_phases_descriptions,
    planets_aspects_descriptions,
    resources_descriptions,
    scripts,
    sun_signs_descriptions,
)
from bot.utils.formatters import date_to_str
from core.models import Client


def get_client_resource(client: Client) -> str:
    if any(int(g) in {22, 36, 12} for g in client.gates):
        return 'мягкость'

    month_numbers_resources = {
        1: 'решимость',
        2: 'мягкость',
        3: 'вдохновение',
        4: 'стойкость',
        5: 'гибкость',
        6: 'принятие',
        7: 'интуиция',
        8: 'границы',
        9: 'ясность',
    }

    return month_numbers_resources.get(
        get_month_number(client.birth.date()),
        'мягкость',
    )


def get_month_resource_text(client: Client):
    sun_sign = [i['sign'] for i in client.planets if i['name'] == 'Sun'][0]
    resource = get_client_resource(client)
    return client.genderize(
        f'{client.fullname.split()[1]}, '
        f'твоя энергия в этом месяце раскрывается через {resource}.\n'
        f'{sun_signs_descriptions[sun_sign]}.\n'
        'Но сейчас ты входишь в новое состояние.\n'
        '*Вот что просит твоя душа услышать:*\n'
        f'{random.choice(resources_descriptions[resource])}\n'
        'Ты не {gender:должен,должна} спешить. Достаточно — быть. И помнить.',
    )


def get_active_hd_gate(date_str=None):
    if date_str is None:
        today = now().strftime('%d.%m.%Y')
    else:
        today = date_str

    today_dt = datetime.strptime(today, '%d.%m.%Y')
    active_date = None
    for hd_date in sorted(hd_gates_descriptions.keys(), reverse=True):
        gate_date = datetime.strptime(hd_date, '%d.%m.%Y')
        if gate_date <= today_dt:
            active_date = hd_date
            break

    if active_date:
        return hd_gates_descriptions[active_date]
    else:
        return None


def get_nearest_sun_aspect(client: Client) -> tuple[str, str]:
    aspects_to_sun = [
        asp
        for asp in client.aspects
        if asp['aspecting_planet'] == 'Sun'
    ]
    if not aspects_to_sun:
        return '', ''
    nearest_aspect = min(aspects_to_sun, key=lambda x: x['orb'])
    return nearest_aspect['aspected_planet'], nearest_aspect['type']


def get_aspect_date(sun: Planet, planet: Planet, aspect_type: str):
    target_angle = aspect_angles.get(aspect_type)
    if target_angle is None:
        return None

    sun_pos = sun.full_degree
    sun_speed = sun.speed
    planet_pos = planet.full_degree
    planet_speed = planet.speed

    # Разница между позициями (нормализованная в пределах 0-360)
    current_diff = (planet_pos - sun_pos) % 360

    # Если текущая разница близка к 360 - считаем как соединение
    if aspect_type == 'Conjunction' and current_diff > 350:
        current_diff = current_diff - 360

    # Разница между текущим углом и целевым аспектом
    angle_diff = (target_angle - current_diff) % 360

    # Если разница > 180, двигаемся в обратном направлении
    if angle_diff > 180:
        angle_diff = angle_diff - 360

    # Если аспект уже точный (допустима погрешность 0.01)
    if abs(angle_diff) < 0.01:
        return datetime.now()

    # Если скорости равны, аспект никогда не наступит
    speed_diff = planet_speed - sun_speed
    if abs(speed_diff) < 0.0001:
        return None

    # Время до аспекта
    days_needed = angle_diff / speed_diff
    if days_needed < 0:
        return None

    return datetime.now() + timedelta(days=days_needed)


async def get_month_script_text(client: Client):
    current_date = date.today().strftime('%m.%Y')

    prev_script = await client.get_previous_month_script()
    if prev_script and prev_script.script_number:
        script_number = random.choice(
            [i for i in range(len(scripts)) if i != prev_script.script_number],
        )
    else:
        script_number = random.randint(0, 5)

    hd_gate = get_active_hd_gate()
    soul_number = get_soul_number(client.fullname)
    moon = moon_phases_descriptions[current_date]

    aspect_planet, aspect_type = get_nearest_sun_aspect(client)
    if aspect_type:
        async with AstrologyAPI() as api:
            planets = {
                p.name: p
                for p in await api.get_tropical_planets(
                    HoroscopeParams.from_client(client),
                )
            }
        aspect_date = get_aspect_date(
            planets['Sun'],
            planets[aspect_planet],
            aspect_type,
        )
    else:
        aspect_date = None

    aspect_text = (
        planets_aspects_descriptions[aspect_planet][aspect_type].format(
            date=date_to_str(aspect_date),
        )
        if aspect_date
        else random.choice(aspect_fallback_texts)
    )

    archetype_of_the_month = month_archetypes_descriptions[current_date]
    archetype_of_the_month = (
        f'{archetype_of_the_month["archetype"]}\n'
        f'{random.choice(archetype_of_the_month["text"])}'
    )

    return client.genderize(
        scripts[script_number].format(
            hd_gate=hd_gate['gate'],
            hd_topic=hd_gate['theme'],
            new_moon_date=moon['new_moon']['date'],
            new_moon_sign=moon['new_moon']['sign'],
            full_moon_date=moon['full_moon']['date'],
            full_moon_sign=moon['full_moon']['sign'],
            archetype_of_the_month=archetype_of_the_month,
            aspect_text=aspect_text,
            balance_tip=random.choice(balance_tips_descriptions[soul_number]),
        ),
    ), script_number
