from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.services.numerology import get_fate_number
from bot.text_templates.base import hd_types_translation
from bot.text_templates.career_and_finance import (
    authorities_descriptions,
    authorities_descriptions_trial,
    fate_numbers_descriptions,
    fate_numbers_descriptions_trial,
    houses_2_descriptions,
    houses_2_descriptions_trial,
    houses_10_descriptions,
    houses_10_descriptions_trial,
    strategies_descriptions,
    strategies_descriptions_trial,
    venus_signs_descriptions,
    venus_signs_descriptions_trial,
)
from core.models import Client


def get_career_and_finance_intro(
    client: Client,
) -> tuple[str, InlineKeyboardMarkup]:
    if not client.is_registered():
        return (
            client.genderize(
                'Хочешь понять, где твои деньги —\n'
                'но {gender:сам,сама} ещё не знаешь, кто ты?\n\n'
                'Пройди регистрацию. Всё начинается с тебя.',
            ),
            get_to_registration_kb(
                back_button_data='to_personal_analysis',
            ),
        )
    elif client.subscription_is_active() or client.has_trial():
        return (
            client.genderize(
                'Ты не для выживания.\n'
                'Ты — для реализации.\n'
                'Я покажу, где твоя энергия превращается в деньги.\n\n'
                '{gender:Готов,Готова} узнать, как монетизируется твоя суть?',
            ),
            one_button_keyboard(
                text='Узнать',
                callback_data='show_career_and_finance',
                back_button_data='to_personal_analysis',
            ),
        )
    else:
        return (
            'Твоя энергия знает, куда ей течь.\n'
            'Осталось только разрешить ей это.\n\n'
            'Оформи доступ — и я покажу, как реализуется твой потенциал.',
            get_to_subscription_plans_kb(
                back_button_data='to_personal_analysis',
            ),
        )


def get_career_and_finance_text(
    client: Client,
) -> str:
    venus_sign = [i for i in client.planets if i['name'] == 'Venus'][0]['sign']
    house_2 = [i for i in client.houses if i['house'] == 2][0]['sign']
    house_10 = [i for i in client.houses if i['house'] == 10][0]['sign']
    fate_number = get_fate_number(client.fullname)
    hd_type = hd_types_translation[client.type]
    if client.subscription_is_active():
        return client.genderize(
            '🚀 Карьера и финансы\n\n'
            'Ты не просто работаешь.\n'
            'Ты выражаешь себя.\n'
            'Каждое твоё решение, каждый шаг — это часть одного большого танца с жизнью.\n'
            'И если ритм собьётся — ты это чувствуешь.\n'
            'Пора снова попасть в такт.\n\n'
            'Деньги — это не просто цифры.\n'
            'Это энергия обмена. Это то, чему ты даёшь вес.\n'
            'Венера рассказывает, как ты выбираешь: за что платить, где быть щедрым, а где — закрыться.\n'
            f'{venus_signs_descriptions[venus_sign]}\n\n'
            'У каждого есть свой код изобилия.\n'
            'И он не в внешнем. Он — в том, как ты создаёшь, как ты опираешься на себя, как ты действуешь.\n'
            f'{houses_2_descriptions[house_2]}\n\n'
            'Ты можешь работать «на кого-то».\n'
            'А можешь — на своё имя.\n'
            '10 дом не говорит, где ты должен быть. Он говорит — какой ты, когда ты на месте.\n'
            f'{houses_10_descriptions[house_10]}\n\n'
            'Мир уже видит тебя.\n'
            'Через манеру, голос, стиль, поведение.\n'
            'И вот как он это считывает:\n'
            f'{fate_numbers_descriptions[fate_number]}\n\n'
            'Слушай… Можно бежать. Можно тянуть. А можно действовать, когда внутри — «да».\n'
            'Твоя стратегия — это не ограничение. Это дверь без замка.\n'
            f'{strategies_descriptions[hd_type]}\n\n'
            'Решения могут казаться логичными.\n'
            'Но ты не логикой сюда {gender:пришёл,пришла}.\n'
            'Твой авторитет — это твой внутренний акселератор.\n'
            f'{authorities_descriptions[client.authority]}\n\n'
            'Ты не {gender:обязан,обязана} пробиваться.\n'
            'Ты можешь просто быть собой — и мир начнёт отзываться.\n'
            'Когда ты на своём месте, деньги приходят не как награда, а как побочный эффект.\n'
            'Так что не строй карьеру. Строй себя.\n'
            'А всё остальное выстроится само.',
        )
    elif client.has_trial():
        return client.genderize(
            '🚀 Карьера и финансы\n\n'
            'Ты по-своему чувствуешь, что «деньги — это...»\n'
            'Для кого-то — контроль. Для тебя, возможно — свобода. Или признание. Или безопасность.\n'
            'Венера показывает: как ты хочешь получать, тратить и наслаждаться.\n'
            f'{venus_signs_descriptions_trial[venus_sign]}\n\n'
            'У тебя свой способ зарабатывать.\n'
            'Он не всегда «по инструкции». Но если идёшь по себе — деньги приходят.\n'
            f'{houses_2_descriptions_trial[house_2]}\n\n'
            'Ты чувствуешь, когда дело “твоё”.\n'
            '10 дом подсказывает, в чём твоя реализация. Где не надо играть, а можно быть собой.\n'
            f'{houses_10_descriptions_trial[house_10]}\n\n'
            'То, как ты входишь в комнату — уже говорит за тебя.\n'
            'В этом числе — твой стиль, харизма, манера действовать.\n'
            f'{fate_number} - {fate_numbers_descriptions_trial[fate_number]}\n\n'
            'Действовать «не вовремя» — значит терять себя.\n'
            'Твоя стратегия — не правило, а подсказка. Она помогает не гнаться, а попадать в точку.\n'
            f'{strategies_descriptions_trial[hd_type]}\n\n'
            'Ум может спорить. Но тело знает.\n'
            'Твой авторитет — как внутренний компас: тихий, но точный.\n'
            f'{authorities_descriptions_trial[client.authority]}\n\n'
            'Ты можешь пробовать всё подряд. А можешь — слушать себя.\n'
            'Когда ты в своей энергии,\n'
            'деньги, дело и признание начинают звучать в унисон.',
        )
