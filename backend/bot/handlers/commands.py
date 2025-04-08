from aiogram import F, Router, flags
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.keyboards.reply import menu_kb
from bot.loader import logger
from core.models import Client

router = Router()


@router.message(Command('start'))
@flags.with_client
async def start(
    msg: Message,
    command: CommandObject,
    client: Client,
    client_created: bool,
):
    if client_created:
        logger.info(f'New client {client} id={client.pk} was created')

        invited_by = (
            await client.check_invitation(command.args)
            if command.args
            else None
        )
        if invited_by:
            logger.info(f'Client {client} was invited by {invited_by}')
    else:
        logger.info(f'Client {client} id={client.pk} was updated')

    await msg.answer(
        f'Привет, {msg.from_user.full_name}!',
        reply_markup=menu_kb,
    )


@router.message(F.text == 'В меню')
async def to_menu(msg: Message):
    await msg.answer('Вы перешли в главное меню', reply_markup=menu_kb)
