import random

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.api.speechkit import synthesize
from bot.keyboards.inline.base import (
    get_to_registration_kb,
    get_to_subscription_plans_kb,
)
from bot.keyboards.inline.friday_gift import friday_gift_kb
from bot.keyboards.utils import one_button_keyboard
from bot.loader import logger
from bot.states import FridayGiftState
from bot.templates.friday_gift import (
    cards,
    friday_gifts_order,
    friday_gifts_preambles,
    insight_phrases,
    symbols,
)
from core.choices import FridayGiftTypes
from core.models import Client, FridayGift, Insight

router = Router()


@router.message(F.text == '🎁 Пятничный подарок')
@flags.with_client
async def friday_gift_intro(msg: Message, client: Client):
    if not client.is_registered():
        await msg.answer(
            '🎁 Пятничный подарок от Soul Muse\n\n'
            'Здесь появляются подарки.\n'
            'Они не про скидки — они про душу.\n'
            'Каждую пятницу Soul Muse приносит знак, образ или фразу — '
            'для тех, кто уже на связи с собой.',
            reply_markup=get_to_registration_kb(
                text='🔒 Зарегистрируйся, чтобы получить свой первый подарок',
            ),
        )
    elif client.subscription_is_active():
        await msg.answer(
            client.genderize(
                '🎁 Пятничный подарок от Soul Muse\n\n'
                'Каждую пятницу Soul Muse вытягивает тебе знак.\n'
                'Иногда это карта. Иногда — образ. Иногда — фраза, которую ты давно {gender:ждал,ждала}.\n'
                'Это не прогноз. Это приглашение прислушаться.\n\n'
                'Открой — если {gender:готов,готова} услышать.',
            ),
            reply_markup=one_button_keyboard(
                text='🎁 Получить подарок недели',
                callback_data='friday_gift',
            ),
        )
    elif client.has_trial():
        await msg.answer(
            '🎁 Пятничный подарок от Soul Muse\n\n'
            'Твоё первое касание с Soul Muse — уже здесь.\n'
            'Я принесла тебе один случайный инсайт.\n'
            'Открой — и посмотри, откликнется ли.',
            reply_markup=one_button_keyboard(
                text='🎁 Получить подарок от Soul Muse',
                callback_data='friday_gift',
            ),
        )
    else:
        await msg.answer(
            client.genderize(
                '🎁 Пятничный подарок от Soul Muse\n\n'
                'Ты уже {gender:получил,получила} подарок.\n'
                'Но Muse не даёт один раз.\n'
                'Каждую пятницу — новый знак. Новый смысл. Новая ты.',
            ),
            reply_markup=get_to_subscription_plans_kb(
                text='🔒 Оформи подписку и получай каждую неделю',
            ),
        )


@router.callback_query(F.data == 'friday_gift')
@flags.with_client
async def friday_gift_handler(query: CallbackQuery, client: Client):
    gift = await FridayGift.objects.get_current_week_gift(client)
    if gift:
        await gift.send(query.message, friday_gift_kb)
        return

    latest_gift = await FridayGift.objects.get_latest_gift(client)
    if latest_gift:
        gift_type = friday_gifts_order[latest_gift.type]
    else:
        gift_type = random.choice(list(FridayGiftTypes.values))

    preamble = client.genderize(friday_gifts_preambles[gift_type])
    if gift_type == FridayGiftTypes.INSIGHT_PHRASES:
        text = ''
        sent_msg = await query.message.answer_audio(
            BufferedInputFile(
                await synthesize(
                    client.genderize(random.choice(insight_phrases)),
                ),
                'Инсайт.wav',
            ),
            caption=preamble,
            reply_markup=friday_gift_kb,
        )
        audio_file_id = sent_msg.audio.file_id
    elif gift_type == FridayGiftTypes.CARDS:
        card = random.choice(cards)
        text = f'Карта «{card["card"].capitalize()}».jpg'
        sent_msg = await query.message.answer_photo(
            BufferedInputFile.from_file('assets/cards/' + text),
            caption=preamble,
            reply_markup=friday_gift_kb,
        )
        audio_file_id = sent_msg.photo[-1].file_id
    elif gift_type == FridayGiftTypes.SYMBOLS:
        text = client.genderize(f'{preamble}\n\n{random.choice(symbols)}')
        await query.message.edit_text(text, reply_markup=friday_gift_kb)
        audio_file_id = None
    else:
        logger.info(f'Invalid gift_type {gift_type!r}')
        return

    await FridayGift.objects.acreate(
        client=client,
        type=gift_type,
        text=text,
        audio_file_id=audio_file_id,
    )


@router.callback_query(F.data == 'respond_to_friday_gift')
async def respond_to_friday_gift(query: CallbackQuery, state: FSMContext):
    await state.set_state(FridayGiftState.insight)
    await query.message.answer(
        'Хочешь оставить отклик этому образу? '
        'Проговори. Или напиши себе — и спрячь на неделю.',
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='delete_this_message_and_clear_state',
        ),
    )


@router.callback_query(F.data == 'delete_this_message_and_clear_state')
async def delete_this_message_and_clear_state(
    query: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await query.message.delete()


@router.message(
    F.text | F.voice,
    F.text != '💫 Премиум-пространство',
    StateFilter(FridayGiftState.insight),
)
async def save_insight(msg: Message, state: FSMContext):
    await Insight.objects.acreate(
        client_id=msg.chat.id,
        text=msg.text or '',
        audio_file_id=msg.voice.file_id if msg.voice else None,
    )
    await msg.answer(
        'Инсайт записан!\nВсе твои инсайты находятся в Soul Space.',
    )
    await state.clear()
