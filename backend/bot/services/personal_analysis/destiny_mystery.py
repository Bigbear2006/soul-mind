from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.services.lunar_nodes import get_lunar_nodes
from bot.services.numerology import (
    get_fate_number,
    get_life_path_number,
    get_soul_number,
)
from bot.text_templates.base import (
    hd_types_translation,
    nodes,
    nodes_trial,
    shadow_archetypes,
    signs_map,
    signs_translation,
)
from bot.text_templates.destiny_mystery import (
    archetypes_descriptions,
    archetypes_descriptions_trial,
    archetypes_in_case,
    hd_profiles,
    hd_profiles_trial,
    hd_types,
    hd_types_trial,
    life_path_numbers,
    life_path_numbers_trial,
    shadow_archetypes_descriptions,
    shadow_archetypes_descriptions_trial,
)
from bot.utils.formatters import your_plural
from core.models import Client


def get_destiny_mystery_intro(
    client: Client,
) -> tuple[str, InlineKeyboardMarkup]:
    if not client.is_registered():
        return (
            'Ты хочешь услышать, зачем ты здесь.\n'
            'Но пока молчит даже твоя Вселенная.\n\n'
            'Пройди регистрацию — и твой путь начнёт разворачиваться.',
            get_to_registration_kb(
                back_button_data='to_personal_analysis',
            ),
        )
    elif client.subscription_is_active() or client.has_trial():
        return (
            client.genderize(
                'Ты {gender:пришёл,пришла} в этот мир не просто жить.\n'
                'Ты — часть замысла.\n'
                'У тебя есть роль, которую не сыграет никто другой.\n'
                'Пора вспомнить её.\n\n'
                'Я покажу тебе, с чего всё началось.',
            ),
            one_button_keyboard(
                text='Узнать',
                callback_data='show_destiny_mystery',
                back_button_data='to_personal_analysis',
            ),
        )
    else:
        return (
            client.genderize(
                'Ты уже {gender:услышал,услышала} зов.\n'
                'И это не отпустит.\n\n'
                'Открой доступ — и я расскажу тебе,\n'
                'почему ты больше, чем кажется.',
            ),
            get_to_subscription_plans_kb(
                back_button_data='to_personal_analysis',
            ),
        )


def get_destiny_mystery_text(client: Client) -> str:
    lpn = get_life_path_number(client.birth.date())
    hd_type = hd_types_translation[client.type]
    soul_number = get_soul_number(client.fullname)
    fate_number = get_fate_number(client.fullname)
    north_node_sign = get_lunar_nodes()['north']
    south_node_sign = signs_map[north_node_sign]

    if client.subscription_is_active():
        hd_profile = hd_profiles[client.profile]
        return client.genderize(
            '🔮 Тайна твоего предназначения\n\n'
            'У каждого — свой маршрут.\n'
            'И всё бы ничего, но ты — не каждый.\n'
            'Ты — из тех, кто пришёл сюда не просто «жить», а вспомнить, зачем пришёл.\n\n'
            f'Я вижу в тебе энергию {archetypes_in_case[soul_number]}.\n'
            f'{archetypes_descriptions[soul_number]}\n\n'
            'Есть и цифры, которые нельзя обмануть.\n'
            f'Твоё число жизненного пути — {lpn}.\n'
            f'{lpn} — {life_path_numbers[lpn]}\n\n'
            f'Ты — {hd_type}.\n'
            'Это значит: у тебя свои правила включения.\n'
            f'{hd_types[hd_type]}\n'
            'И в этом нет ничего нового. Это просто то, кем ты всегда {gender:был,была}\n\n'
            f'Ещё одна подсказка: ты - {hd_profile["profile"]}.\n'
            'Это не о том, кем быть. Это — как быть собой.\n'
            'Через отношения. Через опыт. Через ошибки, которые становятся уроками.'
            f'{hd_profile["description"]}\n'
            'Ты не случайность. Ты — система. С очень красивой логикой.\n\n'
            'А теперь кое-что важное.\n'
            'Лунные узлы — это как навигатор без звука.\n'
            f'{your_plural(south_node_sign)} {signs_translation[south_node_sign]} — где ты уже {{gender:был,была}}, '
            f'где безопасно, но тесно.\n'
            f'{nodes[north_node_sign]["opposite"]}\n'
            f'{your_plural(north_node_sign)} {signs_translation[north_node_sign]}\n'
            '— куда тебя тащит жизнь, даже если ты сопротивляешься.\n'
            'Не потому что "надо". А потому что там — ты.\n'
            f'{nodes[north_node_sign]["self"]}\n\n'
            'Но даже твоя сила может играть против тебя, если ты не слышишь её правильно.\n'
            'Иногда она рулит. Иногда шепчет. Иногда тормозит в самый важный момент.\n'
            f'Когда ты живёшь как {shadow_archetypes[fate_number]} '
            f'{shadow_archetypes_descriptions[fate_number]["description_1"]}\n'
            'И ты можешь бороться с этим вечно — или сказать: «Я больше не верю в эту маску».\n'
            'Потому что ты знаешь, кто за ней.\n'
            f'{shadow_archetypes_descriptions[fate_number]["description_2"]}\n\n'
            'И вот что я хочу, чтобы ты {gender:запомнил,запомнила}:\n'
            'Твоя суть — не в том, кем ты {gender:стал,стала}.\n'
            'А в том, кем ты всегда {gender:был,была}, просто наконец {gender:перестал,перестала} прятаться.',
        )
    elif client.has_trial():
        hd_profile = hd_profiles_trial[client.profile]
        return client.genderize(
            '🔮 Тайна твоего предназначения\n\n'
            'У каждого свой маршрут.\n'
            'Но ты — из тех, кто пришёл сюда не просто «жить». А вспомнить, зачем.\n\n'
            f'В тебе звучит энергия {archetypes_in_case[soul_number]} — не роль, не маска, а направление.\n'
            'Она проявляется в решениях, которые не всегда удобны. Но всегда — настоящие.\n\n'
            f'{archetypes_descriptions_trial[soul_number]}\n\n'
            f'Твоё число жизненного пути — {lpn}\n'
            f'{lpn} — твоя внутренняя настройка.\n'
            'Не «правильный путь», а твой. Если ты в нём — чувствуешь. Если нет — буксуешь.\n'
            f'{life_path_numbers_trial[lpn]}\n\n'
            f'По типу энергии ты — {hd_type}.\n'
            'И у тебя свои правила включения.\n'
            'Когда идёшь вразрез с ними — гаснешь. Когда по ним — светишься.\n'
            f'{hd_types_trial[hd_type]}\n\n'
            f'{hd_profile["profile"]} — твой способ проживать опыт. '
            'Через отношения, вызовы, узнавание себя в людях и ситуациях.\n\n'
            f'{hd_profile["description"]}\n\n'
            'И вот важный ориентир:\n'
            f'{nodes_trial[north_node_sign]}\n\n'
            f'И да, у тебя есть внутренний {shadow_archetypes[fate_number]}.\n'
            'Он может сбивать с маршрута.\n'
            f'{shadow_archetypes_descriptions_trial[fate_number]}\n'
            'Но ты уже знаешь: это не ты. Это старый сценарий, который пора переписать.\n\n'
            'Всё, что ты ищешь — уже в тебе.\n'
            'Я просто перевожу.',
        )
