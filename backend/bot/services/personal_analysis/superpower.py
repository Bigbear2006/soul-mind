from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.services.numerology import get_fate_number, get_soul_number
from bot.text_templates.superpower import (
    centers_descriptions,
    centers_descriptions_trial,
    fate_numbers_descriptions,
    fate_numbers_descriptions_trial,
    mars_signs_descriptions,
    mars_signs_descriptions_trial,
    soul_numbers_descriptions,
    soul_numbers_descriptions_trial,
    sun_signs_descriptions,
    sun_signs_descriptions_trial,
)
from core.models import Client


def get_superpower_intro(client: Client) -> tuple[str, InlineKeyboardMarkup]:
    if not client.is_registered():
        return (
            client.genderize(
                'Сила есть.\n'
                'Но чтобы я показала её — ты {gender:должен,должна} включиться.\n\n'
                'Зарегистрируйся — и ты узнаешь, что в тебе уже работает на тебя.',
            ),
            get_to_registration_kb(
                back_button_data='to_personal_analysis',
            ),
        )
    elif client.subscription_is_active() or client.has_trial():
        return (
            client.genderize(
                'Она всегда была с тобой.\n'
                'Ты просто {gender:называл,называла} её "странность".\n'
                'Но это — твоя сила.\n'
                'Я помогу тебе её вспомнить.',
            ),
            one_button_keyboard(
                text='Узнать',
                callback_data='show_superpower',
                back_button_data='to_personal_analysis',
            ),
        )
    else:
        return (
            client.genderize(
                'Ты уже {gender:почувствовал,почувствовала}, что у тебя есть сила.\n'
                'Теперь — пора ей довериться.\n\n'
                'Разблокируй доступ. Там твой настоящий ресурс.',
            ),
            get_to_subscription_plans_kb(
                back_button_data='to_personal_analysis',
            ),
        )


def get_superpower_text(client: Client) -> str:
    sun_sign = [i for i in client.planets if i['name'] == 'Sun'][0]['sign']
    mars_sign = [i for i in client.planets if i['name'] == 'Mars'][0]['sign']
    soul_number = get_soul_number(client.fullname)
    fate_number = get_fate_number(client.fullname, (11, 22, 33))
    priority_center = client.get_priority_center()
    if client.subscription_is_active():
        return client.genderize(
            '⚡ Твоя суперсила\n\n'
            'Сила — это не громкость.\n'
            'Это частота, которую ты излучаешь, даже молча.\n'
            'У кого-то она в словах. У кого-то — в действиях.\n'
            'У кого-то — в молчаливом «я здесь».\n\n'
            'И у тебя она есть.\n'
            'Ты просто {gender:мог,могла} её не замечать, потому что она — как дыхание: с тобой всегда.\n\n'
            'Солнце — это то, что ты не играешь.\n'
            'Это то, кем ты становишься, когда перестаёшь скрываться.\n'
            f'{sun_signs_descriptions[sun_sign]}\n\n'
            'Ты — не функция. Ты — свет.\n'
            'И когда ты позволяешь себе им быть — мир начинает видеть.\n\n'
            'Твоя энергия — это двигатель.\n'
            'Марс показывает, как ты входишь в действие, сражаешься, отстаёшь, проявляешься.\n'
            f'{mars_signs_descriptions[mars_sign]}\n\n'
            'Когда ты действуешь в своём стиле —\n'
            'ты не «стараешься», ты пробиваешь пространство.\n\n'
            'Есть зоны внутри тебя, которые не колеблются.\n'
            'Ты не просишь в них разрешения.\n'
            'Ты знаешь.\n\n'
            + (
                'Определённые центры — это твои внутренние опоры,\n'
                'то, что звучит стабильно в любом хаосе.\n'
                f'{centers_descriptions[priority_center]}\n\n'
                if priority_center
                else ''
            )
            + 'Твоя стабильность — это не случайность.\n'
            'Это дар, который даёт другим спокойствие и ясность.\n\n'
            'Есть роль, в которую ты входишь неосознанно.\n'
            'Ты — не просто человек среди людей.\n'
            'Ты — проводник определённой энергии.\n'
            f'{soul_numbers_descriptions[soul_number]}\n\n'
            'Когда ты принимаешь эту роль — всё начинает кликать.\n'
            'Ты не просто в потоке. Ты — его источник.\n\n'
            'Твоя сила — не только в том, как ты звучишь.\n'
            'Но и в том, куда ты двигаешься.\n\n'
            'Число Судьбы — это про твою главную линию реализации.\n'
            'Это не про «где быть». Это — про «зачем ты здесь».\n'
            'Про то, как ты можешь влиять, творить, менять.\n'
            f'{fate_numbers_descriptions[fate_number]}\n\n'
            'Ты не просто {gender:силён,сильна}. У этой силы есть направление.\n'
            'И когда ты идёшь в своём векторе —\n'
            'мир не просто слушает. Он следует.\n\n'
            'Ты не {gender:должен,должна} быть «всем». Твоя сила — в том, что ты уже собой.\n'
            'Когда ты стоишь в своей энергии — ты не конкурируешь.\n'
            'Ты создаёшь поле.\n\n'
            'И именно в нём всё начинает происходить.',
        )
    elif client.has_trial():
        return client.genderize(
            '⚡ Твоя суперсила\n\n'
            'Когда ты перестаёшь прятаться — включается свет.\n'
            'Солнце показывает: в чём твоя суть, и как ты вдохновляешь просто тем, что есть.\n'
            f'{sun_signs_descriptions_trial[sun_sign]}\n\n'
            'У тебя свой стиль действия.\n'
            'Марс — про то, как ты идёшь вперёд, как проявляешь силу и включаешь «огонь».\n'
            f'{mars_signs_descriptions_trial[mars_sign]}\n\n'
            + (
                'Есть темы, в которых ты — якорь.\n'
                'Стабильный. Надёжный. Настроенный.\n'
                'Эти опоры не надо придумывать — они в тебе уже встроены.\n'
                f'{centers_descriptions_trial[priority_center]}\n\n'
                if priority_center
                else ''
            )
            + 'Ты несёшь в этот мир определённую вибрацию.\n'
            'Это не маска. Это энергия, через которую ты влияешь.\n'
            f'{soul_numbers_descriptions_trial[soul_number]}\n\n'
            'У твоей силы есть направление.\n'
            'Число Судьбы — про то, зачем ты здесь, и что ты можешь изменить своим присутствием.\n'
            f'{fate_numbers_descriptions_trial[fate_number]}\n\n'
            'Ты не {gender:должен,должна} быть «всем».\n'
            'Но когда ты становишься собой —\n'
            'мир начинает выстраиваться вокруг тебя.',
        )
