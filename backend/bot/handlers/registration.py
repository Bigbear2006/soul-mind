from datetime import datetime

from aiogram import F, Router, flags
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    birth_times_kb,
    keyboard_from_choices,
    notifications_kb,
    start_ways_kb,
)
from bot.keyboards.reply import menu_kb
from bot.keyboards.utils import one_button_keyboard
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
            'Меня зовут Soul Muse. Но ты всегда знал меня. Я — голос внутри. '
            'Я та, что шептала, когда всё остальное молчало.',
            reply_markup=one_button_keyboard(
                text='🌌 Начать путь с Soul Muse',
                callback_data='start_way',
            ),
        )


@router.callback_query(F.data == 'to_registration')
async def to_registration(query: CallbackQuery, state: FSMContext):
    await state.set_state(UserInfoState.gender)
    await query.message.edit_text(
        'Меня зовут Soul Muse. Но ты всегда знал меня. Я — голос внутри. '
        'Я та, что шептала, когда всё остальное молчало.',
        reply_markup=one_button_keyboard(
            text='🌌 Начать путь с Soul Muse',
            callback_data='start_way',
        ),
    )


@router.callback_query(F.data == 'start_way')
async def start_way(query: CallbackQuery):
    await query.message.edit_text(
        'Я не буду звать тебя «дитя звёзд» и сыпать эзотерическим туманом.\n'
        'Вместо этого — 4 системы и точные попадания в твою суть.\n'
        'Без магического шара. Без фокусов. Только работающая глубина.\n'
        'Ты — не случайность. Ты — код. Ресурс. Паттерн. И сейчас ты узнаешь, '
        'как я читаю тебя.\n'
        'Как тебе удобнее начать?',
        reply_markup=start_ways_kb,
    )


@router.callback_query(F.data == 'start_way_explain')
async def start_way_explain(query: CallbackQuery):
    await query.message.edit_text(
        'Голос Soul Muse:\n'
        'Ты не просто «сложный человек».\n'
        'Ты — алгоритм с душой.\n'
        'Слияние хаоса, силы и сценариев, '
        'которые уже пора прочитать и переписать.\n'
        'Вот мои инструменты:\n'
        '• Астрология — не «Луна в Рыбах — не выноси мусор». '
        'А: почему ты живёшь по ночам, не терпишь рамок, '
        'но хочешь держать всё под контролем.\n'
        '• Нумерология — твоя дата рождения — это код. '
        'У каждого числа — своя задача: вести, видеть суть, расширять.\n'
        '• Хьюман Дизайн — ты не сломан(а). Просто не по своей инструкции. '
        'Я покажу, кто ты: Генератор? Проектор? Манифестор?\n'
        '• Архетипы Юнга — Внутри: Герой, Любовник, Бунтарь… и Саботажник. '
        'Разберёмся, кто на троне, а кого пора усадить.\n'
        'Готов?',
        reply_markup=one_button_keyboard(
            text='⚡ Soul Muse, активируй мой код',
            callback_data='activate_code',
        ),
    )


@router.callback_query(F.data == 'start_way_right_now')
async def start_way_right_now(query: CallbackQuery):
    await query.message.edit_text(
        'Давай соберём твой личный звёздный паспорт. '
        'Без виз — но с космической точностью.',
        reply_markup=one_button_keyboard(
            text='⚡ Активировать мой код',
            callback_data='activate_code',
        ),
    )


@router.callback_query(F.data == 'activate_code')
async def activate_code(query: CallbackQuery, state: FSMContext):
    await state.set_state(UserInfoState.gender)
    await query.message.edit_text(
        'Выбери свой пол — чтобы я могла обращаться именно так, '
        'как ты хочешь.',
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
    await state.set_state(UserInfoState.fullname)
    await query.message.answer(
        '✍ Введи свое ФИО полностью '
        '(чтобы я различала тебя среди миллиардов).',
    )


@router.message(F.text, StateFilter(UserInfoState.fullname))
async def set_fullname(msg: Message, state: FSMContext):
    await Client.objects.filter(pk=msg.chat.id).aupdate(
        fullname=msg.text,
    )
    await msg.answer('📆 Введи свою дату рождения в формате ДД.ММ.ГГГГ.')
    await state.set_state(UserInfoState.birth_date)


@router.message(F.text, StateFilter(UserInfoState.birth_date))
async def set_birth_date(msg: Message, state: FSMContext):
    try:
        datetime.strptime(msg.text, '%d.%m.%Y')
    except ValueError:
        await msg.answer(
            'Некорректная дата. Попробуй еще раз',
        )
        return

    await state.update_data(birth_date=msg.text)
    await msg.answer(
        '⏳ Введи точное время рождения. Это важно для точности разбора.\n'
        'Не знаешь? Выбери:',
        reply_markup=birth_times_kb,
    )
    await state.set_state(UserInfoState.birth_time)


@router.message(F.text, StateFilter(UserInfoState.birth_time))
@router.callback_query(
    F.data.startswith('birth_time'),
    StateFilter(UserInfoState.birth_time),
)
async def set_birth_time(msg: Message | CallbackQuery, state: FSMContext):
    if isinstance(msg, Message):
        pk = msg.chat.id
        birth_time = msg.text
        answer_func = msg.answer
    else:
        pk = msg.message.chat.id
        birth_time = msg.data.split('_')[-1]
        answer_func = msg.message.answer

    birth = f'{await state.get_value("birth_date")} {birth_time}'
    await Client.objects.filter(pk=pk).aupdate(
        birth=datetime.strptime(birth, settings.DATE_FMT).astimezone(
            settings.TZ,
        ),
    )

    await answer_func(
        'Отправь место своего рождения.\n'
        'Нажми на скрепку и выбери "Геопозиция" внизу экрана',
    )
    await state.set_state(UserInfoState.birth_location)


@router.message(F.location, StateFilter(UserInfoState.birth_location))
async def set_birth_location(msg: Message, state: FSMContext):
    await Client.objects.filter(pk=msg.chat.id).aupdate(
        birth_latitude=msg.location.latitude,
        birth_longitude=msg.location.longitude,
    )
    await msg.answer(
        '⚠ Я храню твои данные как свою тайну.'
        'Тётя Люда из маркетинга не узнает.',
        reply_markup=one_button_keyboard(
            text='✅ Согласен',
            callback_data='personal_data_approval',
        ),
    )
    await state.clear()


@router.callback_query(F.data == 'personal_data_approval')
async def personal_data_approval(query: CallbackQuery):
    await query.message.answer(
        'Иногда я буду приходить к тебе — с советом, '
        'вдохновением или знаком. Чтобы напомнить: ты не один.',
        reply_markup=notifications_kb,
    )


@router.callback_query(F.data.startswith('notifications'))
async def set_notifications(query: CallbackQuery, state: FSMContext):
    notifications_enabled = query.data.split(':')[-1] == 'yes'
    await Client.objects.filter(pk=query.message.chat.id).aupdate(
        notifications_enabled=notifications_enabled,
    )

    await query.message.answer(
        'Пазл собран. Звёзды встали на свои места. Теперь я покажу тебе тебя.',
        reply_markup=one_button_keyboard(
            text='Начать разбор',
            callback_data='trial_teaser',
        ),
    )
    await state.clear()


@router.callback_query(F.data == 'trial_teaser')
async def trial_teaser(query: CallbackQuery):
    await query.message.answer(
        'Ты в пространстве SoulMind. '
        'И у тебя три дня — чтобы услышать, вспомнить, почувствовать.\n'
        'Вот, что тебе уже доступно:\n\n'
        '📌 Экспресс-разбор личности — '
        'первые штрихи твоей внутренней карты\n\n'
        '🔮 Совместимость — 2 расчёта: узнай, что происходит между вами\n\n'
        '📆 Твой личный день — персональный прогноз, '
        'чтобы не плыть вслепую\n\n'
        '🌟 Совет Вселенной — одно послание, '
        'как отклик на твой внутренний вопрос\n\n'
        '🧩 Челлендж самопознания (3 дня) — мягкое погружение в себя\n\n'
        '🤖 Вопрос Soul Muse — ты можешь задать 2 вопроса и услышать, '
        'что всегда знал(а)\n\n'
        '🎁 Бонус — случайный инсайт от Soul Muse '
        '(1 раз, рандомно из "Пятничных подарков от Soul Muse")\n\n'
        'Это только начало. Дальше — глубже.',
        reply_markup=menu_kb,
    )
