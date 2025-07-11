from datetime import date

from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message
from django.utils.timezone import now

from bot.keyboards.inline.base import get_to_registration_kb
from bot.keyboards.utils import one_button_keyboard
from bot.text_templates.universe_advice import universe_advices
from core.choices import Actions
from core.models import Client, ClientAction

router = Router()


@router.message(F.text == '🌟 Совет Вселенной')
@flags.with_client
async def universe_advice_intro(msg: Message, client: Client):
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


@router.callback_query(F.data == 'universe_advice')
@flags.with_client
async def universe_advice(query: CallbackQuery, client: Client):
    await query.message.edit_text(
        universe_advices.get(
            date.today().strftime('%d.%m.%Y'),
            'К сожалению, на сегодняшний день совета нет.',
        ),
    )
    await ClientAction.objects.aget_or_create(
        client=client,
        action=Actions.UNIVERSE_ADVICE,
        date__date=now().date(),
    )
