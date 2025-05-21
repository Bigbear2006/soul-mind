import asyncio
import random

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from bot.api.speechkit import synthesize
from bot.keyboards.inline.vip_services import get_end_consult_kb
from bot.keyboards.utils import keyboard_from_choices
from bot.loader import logger
from bot.states import MiniConsultState
from bot.templates.vip_services import mosaic_intros, mosaic_experts_texts
from core.choices import MiniConsultFeedbackRatings
from core.models import Client, ExpertAnswer, MiniConsult

router = Router()


@router.callback_query(F.data.startswith('answer_consult'))
async def answer_consult(query: CallbackQuery, state: FSMContext):
    if await state.get_state() == MiniConsultState.answer_consult.state:
        await query.message.answer(
            'Чтобы ответить на эту консультацию, '
            'сначала завершите текущую консультацию',
        )
        return

    consult_id = int(query.data.split(':')[1])
    await state.update_data(consult_id=consult_id)
    await state.set_state(MiniConsultState.answer_consult)
    await query.message.reply(
        'Запишите несколько голосовых сообщений',
        reply_markup=get_end_consult_kb(consult_id),
    )


@router.message(F.voice, StateFilter(MiniConsultState.answer_consult))
async def expert_answer(msg: Message, state: FSMContext):
    await ExpertAnswer.objects.acreate(
        expert=await Client.objects.aget(pk=msg.from_user.id),
        consult=await MiniConsult.objects.aget(
            pk=await state.get_value('consult_id'),
        ),
        audio_file_id=msg.voice.file_id,
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
        '🔥 Ответ готов. Soul Muse ждёт тебя внутри.'
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

    await MiniConsult.objects.filter(pk=consult.pk).aupdate(completed=True)
    await query.bot.send_message(
        consult.client.pk,
        'Как тебе консультация?',
        reply_markup=keyboard_from_choices(
            MiniConsultFeedbackRatings,
            prefix=f'feedback:{consult.pk}',
        ),
    )
    if MiniConsult.objects.filter(client=consult.client).acount() % 3 == 0:
        consults = MiniConsult.objects.prefetch_related('topics').filter(
            client=consult.client,
        )
        experts_text = "\n".join({mosaic_experts_texts[i.expert_type] async for i in consults})
        all_topics = [t for i in consults for t in i.topics.all()]
        if len(all_topics) < 3:
            topics_text = '\n'.join(all_topics)
        else:
            topics_text = '\n'.join(random.choices(all_topics, k=3))
        text = (
            f'{random.choice(mosaic_intros)}\n'
            f'{experts_text}\n'
            f'{topics_text}'
        )
        await query.bot.send_audio(
            consult.client.pk,
            BufferedInputFile(await synthesize(text), 'Мозаика Я.wav')
        )

    await query.message.edit_text('Консультация завершена')
