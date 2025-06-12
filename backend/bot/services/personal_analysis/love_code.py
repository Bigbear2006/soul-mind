from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.services.numerology import get_personality_number, get_soul_number
from bot.text_templates.love_code import (
    house_7_descriptions,
    house_7_descriptions_trial,
    moon_signs_descriptions,
    moon_signs_descriptions_trial,
    personality_numbers_descriptions,
    personality_numbers_descriptions_trial,
    soul_numbers_descriptions,
    soul_numbers_descriptions_trial,
    venus_signs_descriptions,
    venus_signs_descriptions_trial,
)
from core.models import Client


def get_love_code_intro(client: Client) -> tuple[str, InlineKeyboardMarkup]:
    if not client.is_registered():
        return (
            client.genderize(
                'Ты хочешь любви.\n'
                'Но пока не знаешь, как любишь {gender:сам,сама}.\n\n'
                'Пройди регистрацию — и я покажу твой способ чувствовать.',
            ),
            get_to_registration_kb(
                back_button_data='to_personal_analysis',
            ),
        )
    elif client.subscription_is_active() or client.has_trial():
        return (
            'Ты любишь не как все.\n'
            'Интуитивно. Сильно. Не по правилам.\n'
            'Пора понять, на каком языке говорит твоё сердце.',
            one_button_keyboard(
                text='Узнать',
                callback_data='show_love_code',
                back_button_data='to_personal_analysis',
            ),
        )
    else:
        return (
            client.genderize(
                'Любовь уже постучалась.\n'
                'Ты просто ещё не полностью {gender:открыл,открыла} дверь.\n\n'
                'Позволь себе войти глубже. Я рядом.',
            ),
            get_to_subscription_plans_kb(
                back_button_data='to_personal_analysis',
            ),
        )


def get_love_code_text(client: Client) -> str:
    moon_sign = [i for i in client.planets if i['name'] == 'Moon'][0]['sign']
    venus_sign = [i for i in client.planets if i['name'] == 'Venus'][0]['sign']
    house_7 = [i for i in client.houses if i['house'] == 7][0]['sign']
    soul_number = get_soul_number(client.fullname)
    personality_number = get_personality_number(client.fullname)

    if client.subscription_is_active():
        return client.genderize(
            '❤️ Твой код любви\n\n'
            'Любовь — это не сценарий.\n'
            'Это способ быть увиденным.\n'
            'И иногда, чтобы понять, что ты хочешь в любви,\n'
            'нужно сначала понять — как ты вообще чувствуешь.\n\n'
            'Луна — это не про то, как ты выглядишь в отношениях.\n'
            'А про то, как ты переживаешь внутри.\n'
            f'{moon_signs_descriptions[moon_sign]}\n\n'
            'Твои чувства — не ошибка. Даже если они пугают. Даже если ты не {gender:привык,привыкла} их показывать.\n\n'
            'Ты не просто любишь.\n'
            'Ты любишь по-своему.\n'
            'И Венера показывает, как.\n'
            f'{venus_signs_descriptions[venus_sign]}\n\n'
            'Всё, что тебя цепляет — не случайно. Это зеркало твоей внутренней Венеры.\n\n'
            'Партнёрство — это не «идеальная пара». Это контакт. Это вызов. Это отражение.\n'
            '7 дом говорит о том, каких людей ты притягиваешь и какие сценарии строишь вблизи.\n'
            f'{house_7_descriptions[house_7]}\n'
            'Ты не просто ищешь «того самого». Ты ищешь того, в ком откроешься ты.\n\n'
            'Когда ты влюбляешься, включается не логика, а душа.\n'
            'И у неё — свои запросы.\n'
            f'{soul_numbers_descriptions[soul_number]}\n'
            'Если ты знаешь, чего хочет твоя душа — ты не согласишься на меньшее.\n\n'
            'Ты входишь в отношения не как «просто ты».\n'
            'Ты входишь в определённой роли.\n'
            'Архетип — это не маска. Это настройка.\n'
            f'{personality_numbers_descriptions[personality_number]}\n\n'
            'И когда ты осознаёшь, кто ты в любви — ты перестаёшь терять себя в чужих ролях.\n\n'
            'Ты можешь прятаться.\n'
            'Ты можешь играть «холодного» или «удобного».\n'
            'Но внутри всегда звучит:\n'
            '«Покажи меня. Полностью. Без фильтров».\n'
            'Любовь — это риск. Но только она пробуждает ту часть тебя, которая больше не хочет спать.',
        )
    elif client.has_trial():
        return client.genderize(
            '❤️ Твой код любви\n\n'
            'Твои эмоции — это способ быть.\n'
            'Луна показывает, что делает тебя тёплым, уязвимым, живым.\n'
            f'{moon_signs_descriptions_trial[moon_sign]}\n\n'
            'Ты любишь по-особенному.\n'
            'Венера — про то, как ты проявляешь чувства и что тебе действительно нужно в отношениях.\n'
            f'{venus_signs_descriptions_trial[venus_sign]}\n\n'
            'Ты не просто встречаешь людей.\n'
            'Ты создаёшь с ними динамику.\n'
            '7 дом — про то, с кем ты строишь «мы». И как ты в этом «мы» раскрываешься.\n'
            f'{house_7_descriptions_trial[house_7]}\n\n'
            'Когда ты выбираешь сердцем — включается не голова. Включается душа.\n'
            'И у неё — свои ориентиры.\n'
            f'{soul_numbers_descriptions_trial[soul_number]}\n\n'
            'Ты входишь в отношения с определённой энергией.\n'
            'Это не маска. Это код.\n'
            f'{personality_numbers_descriptions_trial[personality_number]}\n\n'
            'Ты можешь притворяться, что тебе всё равно.\n'
            'Но внутри всегда звучит: «Скажи мне правду. Обними без защиты. Останься, даже если страшно».\n'
            'Это и есть любовь. Без костюмов.',
        )
