from datetime import datetime

from aiogram import F, Router, flags
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.keyboards.inline import keyboard_from_choices
from bot.keyboards.reply import menu_kb
from bot.loader import logger
from bot.settings import settings
from bot.states import UserInfoState
from core.models import Client, Genders

router = Router()


@router.message(Command('start'))
@flags.with_client
async def start(
    msg: Message,
    state: FSMContext,
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

    if client.birth_longitude:
        await msg.answer(
            f'Привет, {msg.from_user.full_name}!',
            reply_markup=menu_kb,
        )
    else:
        await state.set_state(UserInfoState.gender)
        await msg.answer(
            'Для начала нужно заполнить данные.\nУкажите свой пол\n'
            '* Пользуясь ботом, вы даете свое согласие на обработку '
            'персональных данных',
            reply_markup=keyboard_from_choices(Genders),
        )


@router.callback_query(
    F.data.in_(Genders.values),
    StateFilter(UserInfoState.gender),
)
async def set_gender(query: CallbackQuery, state: FSMContext):
    await Client.objects.filter(pk=query.message.chat.id).aupdate(
        gender=query.data,
    )
    await query.message.answer(
        'Укажите свою дату и время рождения.\nПример: 21.01.2000 10:30',
    )
    await state.set_state(UserInfoState.birth_datetime)


@router.message(F.text, StateFilter(UserInfoState.birth_datetime))
async def set_birth_datetime(msg: Message, state: FSMContext):
    try:
        await Client.objects.filter(pk=msg.chat.id).aupdate(
            birth=datetime.strptime(msg.text, settings.DATE_FMT).astimezone(
                settings.TZ,
            ),
        )
    except ValueError:
        await msg.answer(
            'Вы ввели некорректную дату и время. Попробуйте еще раз',
        )
        return

    await msg.answer(
        'Отправьте место своего рождения.\n'
        'Нажмите на скрепку и выберите "Геопозиция" внизу экрана',
    )
    await state.set_state(UserInfoState.birth_location)


@router.message(F.location, StateFilter(UserInfoState.birth_location))
async def set_birth_location(msg: Message, state: FSMContext):
    await Client.objects.filter(pk=msg.chat.id).aupdate(
        birth_latitude=msg.location.latitude,
        birth_longitude=msg.location.longitude,
    )
    await msg.answer('Данные заполнены!', reply_markup=menu_kb)
    await state.clear()


@router.message(F.text == 'В меню')
async def to_menu(msg: Message):
    await msg.answer('Вы перешли в главное меню', reply_markup=menu_kb)


@router.message(F.text == 'rm')
async def rm(msg: Message):
    await msg.answer('rm', reply_markup=ReplyKeyboardRemove())
