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
Ты открыл дверь. И, может быть, не все еще ясно. Но точно — не случайно.
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
