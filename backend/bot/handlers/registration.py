from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from aiogram import F, Router, flags
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from bot.api.astrology import AstrologyAPI
from bot.api.geocoding import GeocodingAPI
from bot.api.humandesign import HumanDesignAPI
from bot.keyboards.inline.registration import (
    birth_times_kb,
    start_ways_kb,
)
from bot.keyboards.reply import menu_kb, start_kb
from bot.keyboards.utils import keyboard_from_choices, one_button_keyboard
from bot.loader import logger
from bot.schemas import HDInputData, HoroscopeParams
from bot.services.source_tag import set_source_tag
from bot.services.tags import get_client_tags
from bot.settings import settings
from bot.states import UserInfoState
from core.models import Client, ClientQuestTag, Genders, QuestTag

router = Router()


@router.message(Command('start'))
async def start(msg: Message, command: CommandObject):
    (
        client,
        created,
    ) = await Client.objects.create_or_update_from_tg_user(
        msg.from_user,
    )
    await client.refresh_limits()

    await set_source_tag(client, command.args)

    if created:
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

    if client.is_registered():
        await msg.answer(
            f'Привет, {msg.from_user.full_name}!',
            reply_markup=menu_kb,
        )
    else:
        await msg.answer_video(
            settings.MEDIA.soul_muse_video,
            caption='Нажимая «🌌 Начать путь с Soul Muse», вы соглашаетесь '
            'с условиями нашего пространства:\n'
            f'<a href="{settings.PRIVACY_POLICY_URL}">Политика конфиденциальности SoulMind</a>\n'
            f'<a href="{settings.PUBLIC_OFFER_URL}">Публичная оферта SoulMind</a>\n',
            parse_mode=ParseMode.HTML,
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
    await query.message.answer(
        'Я не буду звать тебя «дитя звёзд» и сыпать эзотерическим туманом.\n\n'
        'Вместо этого — 4 системы и точные попадания в твою суть.\n\n'
        'Без магического шара. Без фокусов. Только работающая глубина.\n\n'
        'Ты — не случайность. Ты — код. Ресурс. Паттерн. И сейчас ты узнаешь, '
        'как я читаю тебя.\n\n'
        'Как тебе удобнее начать?',
        reply_markup=start_ways_kb,
    )


@router.callback_query(F.data == 'start_way_explain')
async def start_way_explain(query: CallbackQuery, state: FSMContext):
    await state.set_state(UserInfoState.gender)
    await query.message.edit_text(
        'Ты не просто «сложный человек».\n\n'
        'Ты — алгоритм с душой.\n\n'
        'Слияние хаоса, силы и сценариев, '
        'которые уже пора прочитать и переписать.\n\n'
        'Вот мои инструменты:\n\n'
        '• Астрология — не «Луна в Рыбах — не выноси мусор». '
        'А: почему ты живёшь по ночам, не терпишь рамок, '
        'но хочешь держать всё под контролем.\n\n'
        '• Нумерология — твоя дата рождения — это код. '
        'У каждого числа — своя задача: вести, видеть суть, расширять.\n\n'
        '• Хьюман Дизайн — ты не сломан(а). Просто живёшь не по своей инструкции. '
        'Я покажу, кто ты: Генератор? Проектор? Манифестор?\n\n'
        '• Архетипы Юнга — Внутри: Герой, Любовник, Бунтарь… и Саботажник. '
        'Разберёмся, кто на троне, а кого пора усадить.\n\n'
        'Готов?\n\n'
        'Выбери свой пол — чтобы я могла обращаться именно так, '
        'как ты хочешь.',
        reply_markup=keyboard_from_choices(Genders),
    )


@router.callback_query(F.data == 'start_way_right_now')
async def start_way_right_now(query: CallbackQuery, state: FSMContext):
    await state.set_state(UserInfoState.gender)
    await query.message.edit_text(
        'Давай соберём твой личный звёздный паспорт. '
        'Без виз — но с космической точностью.\n\n'
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
        reply_markup=start_kb,
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
        '⏳ Введи точное время рождения в формате 00:00. '
        'Это важно для точности разбора.',
        reply_markup=one_button_keyboard(
            text='Не знаю',
            callback_data='unknown_birth_time',
        ),
    )
    await state.set_state(UserInfoState.birth_time)


@router.callback_query(F.data == 'unknown_birth_time')
async def unknown_birth_time(query: CallbackQuery):
    await query.message.edit_text(
        'Не знаешь? Выбери подходящий интервал, нажав на него:',
        reply_markup=birth_times_kb,
    )


@router.message(F.text, StateFilter(UserInfoState.birth_time))
@router.callback_query(
    F.data.startswith('birth_time'),
    StateFilter(UserInfoState.birth_time),
)
async def set_birth_time(msg: Message | CallbackQuery, state: FSMContext):
    if isinstance(msg, Message):
        try:
            datetime.strptime(msg.text, '%H:%M')
        except ValueError:
            await msg.answer('Некорректное время. Попробуй еще раз')
            return

        birth_time = msg.text
        answer_func = msg.answer
    else:
        birth_time = msg.data.split('_')[-1]
        answer_func = msg.message.answer

    birth = f'{await state.get_value("birth_date")} {birth_time}'
    await state.update_data(birth=birth)
    await answer_func(
        'Отправь место своего рождения.\n📍 Только город — без страны',
    )
    await state.set_state(UserInfoState.birth_location)


@router.message(F.text, StateFilter(UserInfoState.birth_location))
@flags.with_client
async def set_birth_location(msg: Message, client: Client, state: FSMContext):
    fail_text = client.genderize(
        'Я вижу, ты {gender:родился,родилась} в месте, которое не у всех на карте.\n'
        'И это уже делает тебя {gender:интересным,интересной}.\n'
        'Но чтобы точнее считать звёзды и дизайн, мне нужен ближайший город.\n'
        'Укажи его — и мы продолжим путь.',
    )
    msg_to_edit = await msg.answer('Собираю данные...')

    try:
        async with GeocodingAPI() as api:
            lat, lon = await api.get_coordinates(msg.text)
    except IndexError:
        await msg_to_edit.edit_text(fail_text)
        return

    async with AstrologyAPI() as api:
        birth = datetime.strptime(
            await state.get_value('birth'),
            settings.DATE_FMT,
        )
        tzone = await api.get_timezone(lat, lon, birth.date())
        birth = birth.replace(tzinfo=timezone(timedelta(hours=tzone)))

        async with HumanDesignAPI() as hd_api:
            bodygraphs = await hd_api.bodygraphs(
                HDInputData.from_datetime(birth, msg.text),
            )

        horoscope = await api.western_horoscope(
            HoroscopeParams(
                day=birth.day,
                month=birth.month,
                year=birth.year,
                hour=birth.hour,
                min=birth.minute,
                lat=lat,
                lon=lon,
                tzone=tzone,
            ),
        )

    await Client.objects.filter(pk=msg.chat.id).aupdate(
        birth=birth,
        birth_place=msg.text,
        birth_latitude=lat,
        birth_longitude=lon,
        tzone=tzone,
        planets=[asdict(i) for i in horoscope.planets],
        houses=[asdict(i) for i in horoscope.houses],
        aspects=[asdict(i) for i in horoscope.aspects],
        **asdict(bodygraphs),
    )

    await client.arefresh_from_db()
    await ClientQuestTag.objects.abulk_create(
        [
            ClientQuestTag(
                client=client,
                tag=tag,
            )
            async for tag in QuestTag.objects.filter(
                name__in=get_client_tags(client),
            )
        ],
    )

    await msg_to_edit.edit_text(
        client.genderize(
            '<b>📩 Введи свою почту — только для чека, если что-то купишь в боте.</b>\n'
            'Это нужно по закону — чтобы ты {gender:мог,могла} получить подтверждение оплаты.\n'
            '<b>Никаких писем, спама и сюрпризов. Только чек — и тишина.</b>',
        ),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(UserInfoState.email)


@router.message(StateFilter(UserInfoState.email))
async def set_email(msg: Message, state: FSMContext):
    validator = EmailValidator()
    try:
        validator(msg.text)
        await Client.objects.filter(pk=msg.chat.id).aupdate(
            email=msg.text,
            notifications_enabled=True,
        )
    except ValidationError:
        await msg.answer('Некорректная почта. Попробуй ещё раз.')
        return

    await msg.answer(
        '⚠️ Я храню твои данные как свою тайну. '
        'Тётя Люда из маркетинга не узнает.\n'
        'Согласен с обработкой данных в рамках '
        f'<a href="{settings.PRIVACY_POLICY_URL}">Политики</a>',
        parse_mode=ParseMode.HTML,
        reply_markup=one_button_keyboard(
            text='✅ Согласен',
            callback_data='personal_data_approval',
        ),
    )
    await state.clear()


@router.callback_query(F.data == 'personal_data_approval')
async def set_notifications(query: CallbackQuery, state: FSMContext):
    await Client.objects.filter(pk=query.message.chat.id).aupdate(
        notifications_enabled=True,
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
@flags.with_client
async def trial_teaser(query: CallbackQuery, client: Client):
    await query.message.answer(
        client.genderize(
            'Ты в пространстве SoulMind. '
            'И у тебя три дня — чтобы услышать, вспомнить, почувствовать.\n'
            'Вот, что тебе уже доступно:\n\n'
            '📌 Экспресс-разбор личности — '
            'первые штрихи твоей внутренней карты\n\n'
            '🔮 Совместимость — 1 расчёт: узнай, что происходит между вами\n\n'
            '📆 Твой личный день — персональный прогноз, '
            'чтобы не плыть вслепую\n\n'
            '🌟 Совет Вселенной — одно послание, '
            'как отклик на твой внутренний вопрос\n\n'
            '🧩 Челлендж самопознания (3 дня) — мягкое погружение в себя\n\n'
            '👩🏽 Вопрос к Soul Muse — ты можешь задать 1 вопрос и услышать, '
            'что всегда {gender:знал,знала}\n\n'
            '🎁 Бонус — случайный инсайт от Soul Muse\n\n'
            'Это только начало. Дальше — глубже.',
        ),
        reply_markup=menu_kb,
    )
