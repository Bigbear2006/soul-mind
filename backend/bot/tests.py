import asyncio
import os

from bot.templates.friday_gift import cards


def all_cards_has_images():
    l = os.listdir('../assets/cards')
    for card in cards:
        x = f'Карта «{card["card"].capitalize()}».jpg'
        try:
            l.remove(x)
        except ValueError:
            print(x)
    print(l)  # must be empty


all_cards_has_images()


async def test_main():
    async def t1():
        raise KeyError('some key')

    async def t2():
        return 1

    done, pending = await asyncio.wait(
        [asyncio.create_task(i) for i in [t2(), t1(), t2()]],
    )
    print([i.result() for i in done if not i.exception()], pending, sep='\n')


asyncio.run(test_main())
