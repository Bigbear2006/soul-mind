import asyncio
import os

from bot.api.speechkit import synthesize
from bot.templates.friday_gift import cards
from bot.text_utils import split_text


def all_cards_has_images():
    l = os.listdir('assets/cards')
    for card in cards:
        x = f'Карта «{card["card"].capitalize()}».jpg'
        try:
            l.remove(x)
        except ValueError:
            print(x)
    print(l)  # must be empty


async def test_asyncio_wait_ignore_exceptions():
    async def t1():
        raise KeyError('some key')

    async def t2():
        return 1

    done, pending = await asyncio.wait(
        [asyncio.create_task(i) for i in [t2(), t1(), t2()]],
    )
    print([i.result() for i in done if not i.exception()], pending, sep='\n')


text = """
Ты открыл дверь.
И, может быть, не всё ещё ясно. Но точно — не случайно.
То, что ты сейчас держишь перед собой — это приглушённый свет,
который уже зовёт сильнее.
Этот экспресс-отчёт — не про всё.
Но он показывает главное:
У тебя есть код.
У тебя есть настройка.
У тебя есть глубина.
Здесь ты увидишь первые контуры своей карты:
— кем ты был(-а) всегда, просто забыл(-а);
— как звучит твоя энергия в делах, чувствах, решениях;
— и что в тебе уже работает как магнит, даже если ты не знал(-а) об
этом.
SoulMind — это не просто разбор.

Это внутреннее «а-а-а… вот почему я такой(-ая)».
И сейчас ты слышишь только начало.
Но оно — твоё.
 Тайна твоего предназначения
У каждого свой маршрут.
Но ты — из тех, кто пришёл сюда не просто «жить». А вспомнить,
зачем.
В тебе звучит энергия Творца / Архитектора — не роль, не маска, а
направление.
Она проявляется в решениях, которые не всегда удобны. Но всегда —
настоящие.
    """


async def test_speechkit_v3_api():
    print(split_text(text))
    r = await synthesize(text)
    with open('test.wav', 'wb') as f:
        f.write(r)


# async def test_speechkit_v3_rpc():
#     configure_credentials(
#         creds.YandexCredentials(api_key=settings.YANDEX_API_KEY),
#     )
#     model = model_repository.synthesis_model()
#     model.voice = 'zhanar'
#     model.role = 'friendly'
#     r = model.synthesize(text, raw_format=True)
#     with open('v3_rpc.wav', 'wb') as f:
#         f.write(r)
