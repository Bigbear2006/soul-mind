import asyncio
import random

from aiogram import F, Router, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.api.speechkit import synthesize
from bot.keyboards.inline.vip_services import get_end_consult_kb
from bot.keyboards.utils import keyboard_from_choices
from bot.loader import logger
from bot.states import MiniConsultState
from bot.templates.vip_services import mosaic_experts_texts, mosaic_intros, mosaic_topic_texts
from core.choices import MiniConsultFeedbackRatings, MiniConsultStatuses
from core.models import Client, ExpertAnswer, MiniConsult

router = Router()


@router.callback_query(F.data.startswith('answer_consult'))
@flags.with_client
async def answer_consult(query: CallbackQuery, state: FSMContext):
    if await state.get_state() == MiniConsultState.answer_consult.state:
        await query.message.reply(
            'Чтобы ответить на эту консультацию, '
            'сначала завершите текущую консультацию',
        )
        return

    consult = await MiniConsult.objects.aget(pk=int(query.data.split(':')[1]))
    if consult.status != MiniConsultStatuses.WAITING:
        await query.message.reply(
            'Эту консультацию уже взял другой эксперт или она завершена'
        )
        return

    await state.update_data(consult_id=consult.pk)
    await state.set_state(MiniConsultState.answer_consult)
    await query.message.reply(
        'Запишите несколько голосовых сообщений',
        reply_markup=get_end_consult_kb(consult.pk),
    )


@router.message(F.voice, StateFilter(MiniConsultState.answer_consult))
async def expert_answer(msg: Message, state: FSMContext):
    file = await msg.bot.get_file(msg.voice.file_id)
    await ExpertAnswer.objects.acreate(
        expert=await Client.objects.aget(pk=msg.from_user.id),
        consult=await MiniConsult.objects.aget(
            pk=await state.get_value('consult_id'),
        ),
        audio_file_id=msg.voice.file_id,
        audio_file_path=file.file_path,
    )
    await msg.answer('Записано')


@router.callback_query(
    F.data.startswith('end_consult'),
    StateFilter(MiniConsultState.answer_consult),
)
async def end_consult(query: CallbackQuery, state: FSMContext):
    consult = await MiniConsult.objects.select_related('client').aget(
        pk=await state.get_value('consult_id'),
    )
    answers = ExpertAnswer.objects.filter(consult=consult)

    if await answers.acount() == 0:
        await query.message.answer(
            'Нужно записать как минимум одно голосовое сообщение!',
        )
        return

    await query.bot.send_message(
        consult.client.pk,
        '🔥 Ответ готов. Soul Muse ждёт тебя внутри.',
    )
    async for answer in answers:
        try:
            await query.bot.send_audio(
                consult.client.pk,
                audio=answer.audio_file_id,
            )
            await asyncio.sleep(1)
        except TelegramBadRequest as e:
            logger.exception(
                f'Error in sending mini consult answers: '
                f'{e.__class__.__name__}: {str(e)}',
            )

    await MiniConsult.objects.filter(pk=consult.pk).aupdate(status=MiniConsultStatuses.COMPLETED)
    await query.bot.send_message(
        consult.client.pk,
        'Как тебе консультация?',
        reply_markup=keyboard_from_choices(
            MiniConsultFeedbackRatings,
            prefix=f'feedback:{consult.pk}',
        ),
    )

    if await MiniConsult.objects.filter(client=consult.client).acount() % 3 == 0:
        consults = MiniConsult.objects.prefetch_related('topics').filter(
            client=consult.client,
        )
        experts_text = '\n'.join(
            {mosaic_experts_texts[i.expert_type] async for i in consults},
        )
        all_topics = [
            mosaic_topic_texts[t]
            for i in consults for t in i.topics.all()
            if t in mosaic_topic_texts
        ]
        if len(all_topics) < 3:
            topics_text = '\n'.join(all_topics)
        else:
            topics_text = '\n'.join(random.choices(all_topics, k=3))
        text = f'{random.choice(mosaic_intros)}\n{experts_text}\n{topics_text}'
        await query.bot.send_audio(
            consult.client.pk,
            BufferedInputFile(await synthesize(text), 'Мозаика Я.wav'),
        )

    await query.message.edit_text('Консультация завершена')
