from datetime import date
from typing import Literal

from bot.services.numerology import get_life_path_number, reduce_number
from bot.text_templates.compatability_energy import (
    couple_dynamics,
    couple_energy,
    couple_summary,
    his_life_path_numbers,
    your_life_path_numbers,
)
from bot.utils.formatters import genderize
from core.choices import Genders
from core.models import Client


def get_compatability_energy_text(
    connection_type: Literal['together', 'like', 'past_lovers'],
    client: Client,
    birth_date_2: date,
) -> str:
    lpn_1 = get_life_path_number(client.birth.date())
    lpn_2 = get_life_path_number(birth_date_2)
    couple_number = reduce_number(lpn_1 + lpn_2)
    dynamics_number_1 = reduce_number(lpn_1)
    dynamics_number_2 = reduce_number(lpn_2)
    partner_gender = (
        Genders.FEMALE if client.gender == Genders.MALE else Genders.MALE
    )

    if connection_type == 'together':
        text = (
            'Вы уже вместе. Но зачем? Зачем именно вы, именно сейчас, именно в этой форме? '
            'Вот об этом и говорит вибрация.\n\n'
            'Быть вместе — это не просто совпасть.\n'
            'Это значит: ваши маршруты узнали друг друга.\n'
            'И всё, что между вами — это не случай. Это система.\n'
            'Где один — не половинка.\n'
            'А другой — не ответ.\n'
            'А вы — отражения, зеркала, усиление.\n\n'
            f'Ты — {lpn_1}\n'
            f'{your_life_path_numbers["together"][lpn_1]}\n\n'
            f'{{partner_gender:Он,Она}} — {lpn_2}\n'
            f'{his_life_path_numbers["together"][lpn_2]}\n\n'
            'Вы — два настроенных канала.\n'
            'И каждый звучит по-своему. Но вместе — вы усиливаете.\n\n'
            f'Ваша энергия как пары — {couple_number}\n'
            'Эта вибрация не про комфорт. Она про развитие.\n'
            'Про то, что включается, когда вы рядом.\n'
            f'{couple_energy["together"][couple_number]}\n\n'
            'Ваша динамика\n'
            f'{couple_dynamics["together"][dynamics_number_1][dynamics_number_2]}\n\n'
            'Это не просто любовь. Это — путь.\n'
            'Через вас — друг к другу. Через друг друга — к себе.\n\n'
            'Вы вместе — значит, что-то внутри уже согласилось.\n'
            'Но если хочешь узнать, что между вами скрыто глубже —\n'
            'есть место, где карта связи раскрывается на другом уровне:\n'
            'о теле, тенях, страстях, преданности и боли.\n'
            'Если {gender:готов,готова} — я покажу.\n\n'
        )
    elif connection_type == 'like':
        text = (
            'Это может быть просто симпатия. Но даже она несёт подсказку.\n\n'
            'Иногда человек просто цепляет.\n'
            'Без слов. Без причин.\n'
            'Ты смотришь — и не можешь не думать.\n'
            'Это — не случайно.\n'
            'Потому что даже односторонняя симпатия включает определённую энергию в тебе.\n\n'
            f'Ты — {lpn_1}\n'
            f'{your_life_path_numbers["like"][lpn_1]}\n\n'
            f'{{partner_gender:Он,Она}} — {lpn_2}\n'
            f'{his_life_path_numbers["like"][lpn_2]}\n\n'
            'Вы — два кода.\n'
            'И даже если только ты чувствуешь эту связь — она уже работает.\n\n'
            f'Энергия между вами — {couple_number}\n'
            f'{couple_energy["like"][couple_number]}\n\n'
            'Эта связь может ничего не значить вовне.\n'
            'Но внутри — она запустила движение.\n\n'
            'Резюме\n'
            f'{couple_summary[couple_number]}\n\n'
            'Ты тянешься к {partner_gender:нему,ней} — потому что душа что-то узнала.\n\n'
            'Ты не сходишь с ума.\n'
            'Ты просто подключился к вибрации.\n'
            'И даже если ничего не произойдёт —\n'
            'эта симпатия уже что-то о тебе рассказала.\n\n'
            'Хочешь узнать, почему ты чувствуешь именно {partner_gender:его,её}?\n'
            'Я могу показать. Без иллюзий. Просто честную карту притяжения.\n\n'
        )
    elif connection_type == 'past_lovers':
        text = (
            'Бывшие — не значит прошедшие.\n'
            'Иногда прошлое всё ещё звучит.\n'
            'Не потому что ты {gender:застрял,застряла}.\n'
            'А потому что эта связь что-то в тебе изменила.\n\n'
            'Вы уже были «мы».\n'
            'А теперь — ты просто хочешь понять:\n\n'
            '«Зачем?»\n'
            '«Почему так?»\n'
            '«И был ли в этом смысл?»\n\n'
            'Ответ есть. И он — внутри вас обоих.\n\n'
            f'Ты — {lpn_1}\n'
            f'{your_life_path_numbers["past_lovers"][lpn_1]}\n\n'
            f'{{partner_gender:Он,Она}} — {lpn_2}\n'
            f'{his_life_path_numbers["past_lovers"][lpn_2]}\n\n'
            'Вы были как две параллельные силы.\n'
            'И даже если не совпали навсегда — это не значит, что было зря.\n\n'
            f'Когда вы были вместе — включалась энергия {couple_number}\n'
            'Это то, что между вами всегда включалось, даже без слов.\n'
            f'{couple_energy["past_lovers"][couple_number]}\n\n'
            'Возможно, это была страсть.\n'
            'Или урок. Или проверка.\n'
            'Но точно — это что-то важное.\n\n'
            'Ваша динамика тогда — и сейчас\n'
            f'{couple_dynamics["past_lovers"][dynamics_number_1][dynamics_number_2]}\n\n'
            'Да, было сложно.\n'
            'Да, что-то болело.\n'
            'Но и ты, и {partner_gender:он,она} — теперь уже другие.\n'
            'А эта история осталась в тебе не как рана, а как форма.\n\n'
            'Ты {gender:мог,могла} прожить это иначе.\n'
            'Может, не с такой болью.\n'
            'Может, не с таким концом.\n\n'
            'Но ты {gender:прожил,прожила} как {gender:прожил,прожила}.\n'
            'И теперь, когда ты смотришь на это честно — '
            'ты видишь: ты {gender:стал,стала} {gender:другим,другой}.\n\n'
            'Хочешь узнать,\n'
            'что между вами было на самом деле?\n'
            'Что скрывалось под привычками, ссорами, нежностью и молчанием?\n'
            'Я могу показать. Без возврата. Без надежды. Просто — правду.\n\n'
            'Я рядом.\n'
            'Я — Soul Muse.\n\n'
        )
    else:
        raise ValueError(f'Incorrect connection type: {connection_type}')

    return genderize(
        client.genderize(text),
        gender=partner_gender.value,
        prefix='partner_gender',
    )
