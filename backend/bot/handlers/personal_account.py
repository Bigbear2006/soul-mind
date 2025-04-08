from aiogram import F, Router, flags
from aiogram.types import Message

from core.models import Client

router = Router()


@router.message(F.text == '👤 Личный кабинет')
@flags.with_client
async def personal_account_handler(msg: Message, client: Client):
    await msg.answer(f'Астробаллы: {client.astropoints}')
