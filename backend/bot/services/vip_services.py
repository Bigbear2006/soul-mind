import random

from aiogram.types import BufferedInputFile, Message

from bot.api.soul_muse import SoulMuse
from bot.api.speechkit import synthesize
from bot.prompts.personal_report import get_personal_report_prompt
from bot.text_templates.vip_services import (
    personal_report_audio_closures,
    personal_report_intro,
)
from bot.utils.pdf import generate_pdf
from core.models import Client


async def make_vip_report(msg: Message, client: Client):
    report = await SoulMuse().answer(get_personal_report_prompt(client))
    pdf_text = personal_report_intro + report
    audio_text = f'{report}\n{random.choice(personal_report_audio_closures)}'
    await msg.answer_document(
        BufferedInputFile(generate_pdf(pdf_text), 'Персональный отчёт.pdf'),
    )
    await msg.answer_audio(
        BufferedInputFile(
            await synthesize(audio_text),
            'Персональный отчёт.wav',
        ),
    )
