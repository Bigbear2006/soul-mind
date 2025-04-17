from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.inline import get_to_registration_kb
from bot.keyboards.utils import one_button_keyboard
from core.models import Client

router = Router()


@router.message(F.text == '🌟 Совет Вселенной')
async def universe_advice(msg: Message):
    client: Client = await Client.objects.aget(pk=msg.chat.id)

    if not client.is_registered():
        await msg.answer(
            '🌟 Совет Вселенной\n\n'
            'Вселенная уже готова сказать тебе кое-что важное.\n'
            'Но чтобы услышать — тебе нужно появиться.\n\n'
            'Зарегистрируйся — и каждое утро тебя будет ждать послание.',
            reply_markup=get_to_registration_kb(),
        )
    else:
        await msg.answer(
            '🌟 Совет Вселенной\n\n'
            'Вселенная говорит с теми, кто умеет слушать.\n'
            'Каждое утро — одно послание.\n'
            'Короткое. Точное. В нужный момент.\n\n'
            'Хочешь услышать, на что стоит обратить внимание сегодня?',
            reply_markup=one_button_keyboard(
                text='🌀 Получить совет',
                callback_data='universe_advice',
            ),
        )
