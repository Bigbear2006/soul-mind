from dataclasses import asdict
from datetime import datetime

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    Message,
)

from bot.api.humandesign import HumanDesignAPI
from bot.api.soul_muse import SoulMuse
from bot.api.speechkit import synthesize
from bot.keyboards.inline.registration import birth_times_kb
from bot.keyboards.inline.vip_services import (
    connection_types_kb,
    get_answer_consult_kb,
    get_payment_choices_kb,
    get_topics_kb,
    get_vip_compatability_report_kb,
    vip_services_kb,
)
from bot.keyboards.utils import (
    keyboard_from_choices,
    one_button_keyboard,
)
from bot.prompts.vip_compatability import get_vip_compatability_prompt
from bot.schemas import Bodygraphs, HDInputData
from bot.services.payment import check_payment, send_payment_link
from bot.services.vip_services import make_vip_report
from bot.settings import settings
from bot.states import (
    MiniConsultState,
    PersonalReportState,
    VIPCompatabilityState,
)
from bot.text_templates.base import astropoints_not_enough, connection_types
from bot.text_templates.vip_services import ask_question_instructions
from bot.utils.pdf import generate_pdf
from bot.utils.validation import validate_time
from core.choices import (
    ExperienceTypes,
    ExpertTypes,
    FeelingsTypes,
    Intentions,
    PurchaseTypes,
)
from core.models import (
    Client,
    ExpertType,
    MiniConsult,
    MiniConsultFeedback,
    MiniConsultTopic,
    Purchase,
    Topic,
)

router = Router()


@router.message(F.text == 'VIP-Услуги')
@router.callback_query(F.data == 'vip_services')
async def vip_services_handler(msg: Message | CallbackQuery):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    await answer_func(
        '💎 VIP-Услуги от Soul Muse\n\n'
        'У каждого — свой запрос.\n'
        'Иногда он требует большего пространства.\n'
        'Разбор только о тебе. Голос только для тебя.\n'
        'Глубже. Ближе.\n'
        'Выбирай, что откликается.',
        reply_markup=vip_services_kb,
    )


####################
### MINI CONSULT ###
####################


@router.callback_query(F.data == 'vip_mini_consult')
async def vip_mini_consult(callback: CallbackQuery):
    await callback.message.edit_text(
        '🎧 Мини-консультация с экспертом\n\n'
        'У тебя есть вопрос, и он требует живого голоса.\n'
        '- Астролог\n- Нумеролог\n- Эксперт по Хьюман-дизайну\n'
        '- Психолог\n- Духовный наставник-энергопрактик\n\n'
        '3–5 голосовых от того, кто умеет читать глубже.',
        reply_markup=one_button_keyboard(
            text='999 ₽',
            callback_data='buy_mini_consult',
            back_button_data='vip_services',
        ),
    )


@router.callback_query(F.data == 'buy_mini_consult')
async def buy_mini_consult(query: CallbackQuery, state: FSMContext):
    await state.set_state(MiniConsultState.payment_type)
    await query.message.answer(
        'Выбери тип оплаты',
        reply_markup=get_payment_choices_kb(
            None,
            '999 ₽',
        ),
    )


@router.callback_query(
    F.data.in_(('astropoints', 'money')),
    StateFilter(MiniConsultState.payment_type),
)
@flags.with_client
async def choose_mini_consult_payment_type(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    if query.data == 'astropoints':
        if client.astropoints < 1500:
            await query.message.edit_text(
                astropoints_not_enough,
                reply_markup=get_payment_choices_kb(None, '999 ₽'),
            )
            return
        client.astropoints -= 1500
        await client.asave()
        await query.message.edit_text(
            'Выбери тип эксперта',
            reply_markup=keyboard_from_choices(ExpertTypes, prefix='expert'),
        )
        await state.clear()
    else:
        await state.set_state(MiniConsultState.payment)
        await send_payment_link(
            query,
            state,
            amount=999,
            description='Мини-консультация с экспертом',
            email=client.email,
        )


@router.callback_query(
    F.data == 'check_buying',
    StateFilter(MiniConsultState.payment),
)
@flags.with_client
async def choose_expert_type(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await check_payment(query, state)
    await Purchase.objects.from_client(
        client,
        PurchaseTypes.MINI_CONSULT,
    )
    await query.message.edit_text(
        'Выбери тип эксперта',
        reply_markup=keyboard_from_choices(ExpertTypes, prefix='expert'),
    )


@router.callback_query(F.data.startswith('expert'))
async def choose_intention(query: CallbackQuery, state: FSMContext):
    await state.update_data(expert_type=query.data.split(':')[1])
    await state.set_state(MiniConsultState.intention)
    await query.message.edit_text(
        'Выбери свое намерение\n'
        'Если его нет в списке, можешь ввести свой вариант.',
        reply_markup=keyboard_from_choices(Intentions, prefix='intention'),
    )


@router.message(F.text, StateFilter(MiniConsultState.intention))
@router.callback_query(
    F.data.startswith('intention'),
    StateFilter(MiniConsultState.intention),
)
async def choose_experience_type(
    msg: Message | CallbackQuery,
    state: FSMContext,
):
    if isinstance(msg, Message):
        answer_func = msg.answer
        intention = msg.text
    else:
        answer_func = msg.message.answer
        intention = Intentions(msg.data.split(':')[1]).label

    await state.update_data(intention=intention)
    await answer_func(
        'Ты уже сталкивался с этим направлением?',
        reply_markup=keyboard_from_choices(
            ExperienceTypes,
            prefix='experience',
        ),
    )


@router.callback_query(F.data.startswith('experience'))
async def choose_feelings_type(query: CallbackQuery, state: FSMContext):
    await state.update_data(experience_type=query.data.split(':')[1])
    await query.message.edit_text(
        'Как ты сейчас себя ощущаешь?',
        reply_markup=keyboard_from_choices(FeelingsTypes, prefix='feelings'),
    )


@router.callback_query(F.data.startswith('feelings'))
@flags.with_client
async def choose_topics(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await state.update_data(feelings_type=query.data.split(':')[1])
    await state.set_state(MiniConsultState.topics)
    await query.message.edit_text(
        'Выбери до трех меток, к которым относится твой вопрос.\n'
        'Если нужной метки нет в списке, то можешь написать ее.',
        reply_markup=await get_topics_kb(client),
    )


@router.message(F.text, StateFilter(MiniConsultState.topics))
@router.callback_query(
    F.data.startswith('topic'),
    StateFilter(MiniConsultState.topics),
)
@flags.with_client
async def ask_question(
    msg: Message | CallbackQuery,
    state: FSMContext,
    client: Client,
):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.answer
    )

    pk = msg.data.split(':')[1] if isinstance(msg, CallbackQuery) else ''
    data = await state.get_data()
    topics = data.get('topics', [])
    if pk != 'done' or len(topics) == 3:
        if isinstance(msg, Message):
            topic, created = await Topic.objects.aget_or_create(name=msg.text)
        else:
            topic = await Topic.objects.aget(pk=pk)
        topics.append(topic.pk)
        await state.update_data(topics=topics)
        await answer_func(f'Метка {client.genderize(topic.name)} добавлена')

    if pk == 'done' or len(topics) == 3:
        if data['expert_type'] == ExpertTypes.SPIRITUAL_MENTOR:
            await state.set_state(MiniConsultState.photo)
            await answer_func(
                '🌿 Для настройки на твоё поле нужно фото.\n'
                'Не архивное, а живое — недавнее, без фильтров.\n'
                'Только чтобы почувствовать тебя — здесь и сейчас.\n'
                'Фото нигде не сохраняется, используется только для ответа.',
            )
            return

        await state.set_state(MiniConsultState.question)
        await answer_func(ask_question_instructions)


@router.message(StateFilter(MiniConsultState.photo))
async def set_photo(msg: Message, state: FSMContext):
    if not msg.photo:
        await msg.answer('Не могу найти фото в сообщении. Попробуй еще раз.')
        return

    await state.update_data(photo_file_id=msg.photo[-1].file_id)
    await state.set_state(MiniConsultState.question)
    await msg.answer(ask_question_instructions)


@router.message(F.text | F.voice, StateFilter(MiniConsultState.question))
@flags.with_client
async def send_question_to_expert(
    msg: Message,
    state: FSMContext,
    client: Client,
):
    data = await state.get_data()
    topics_ids = data.get('topics', [])

    if msg.voice:
        file_path = (await msg.bot.get_file(msg.voice.file_id)).file_path
    else:
        file_path = ''

    consult = await MiniConsult.objects.acreate(
        client=client,
        text=msg.text or '',
        audio_file_id=msg.voice.file_id if msg.voice else None,
        audio_file_path=file_path,
        photo_file_id=data.get('photo_file_id', None),
        expert_type=await ExpertType.objects.aget(name=data['expert_type']),
        intention=data['intention'],
        experience_type=data['experience_type'],
        feelings_type=data['feelings_type'],
    )
    await MiniConsultTopic.objects.abulk_create(
        [MiniConsultTopic(consult=consult, topic_id=t) for t in topics_ids],
    )

    consult = (
        await MiniConsult.objects.select_related('client', 'expert_type')
        .prefetch_related('topics__topic')
        .aget(pk=consult.pk)
    )

    async for client in Client.objects.filter(
        expert_types__expert_type=consult.expert_type,
    ):
        await consult.send_to(
            chat_id=client.id,
            reply_markup=get_answer_consult_kb(consult),
        )

    await msg.answer('Вопрос принят. Эксперт ответит в течение 24 часов.')
    await state.clear()


@router.callback_query(F.data.startswith('feedback'))
async def send_feedback(query: CallbackQuery, state: FSMContext):
    _, consult_id, rating = query.data.split(':')
    await state.update_data(consult_id=consult_id, rating=rating)
    await state.set_state(MiniConsultState.comment)
    await query.message.edit_text(
        'Можешь записать голосовое или написать комментарий о консультации',
        reply_markup=one_button_keyboard(
            text='Не оставлять комментарий',
            callback_data='send_feedback_without_comment',
        ),
    )


@router.callback_query(F.data == 'send_feedback_without_comment')
async def send_feedback_without_comment(
    query: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    await MiniConsultFeedback.objects.acreate(
        consult_id=data['consult_id'],
        rating=data['rating'],
    )
    await query.message.edit_text('Ответ записан!')
    await state.clear()


@router.message(F.text | F.voice, StateFilter(MiniConsultState.comment))
async def send_feedback_with_comment(msg: Message, state: FSMContext):
    data = await state.get_data()

    if msg.voice:
        file_path = (await msg.bot.get_file(msg.voice.file_id)).file_path
    else:
        file_path = ''

    await MiniConsultFeedback.objects.acreate(
        consult_id=data['consult_id'],
        rating=data['rating'],
        audio_file_id=msg.voice.file_id if msg.voice else None,
        audio_file_path=file_path,
        text=msg.text or '',
    )
    await msg.answer('Ответ записан!')
    await state.clear()


###########################
### VIP PERSONAL REPORT ###
###########################


@router.callback_query(F.data == 'vip_personal_report')
async def vip_personal_report(callback: CallbackQuery):
    await callback.message.edit_text(
        '📄 Глубокий персональный отчёт\n\n'
        'Ты хочешь не просто вдохновение — ты хочешь ориентиры.\n'
        'Этот отчёт — как карта с метками: где ты сейчас, куда направлена твоя энергия,\n'
        'и что важно не пропустить в этом месяце.\n\n'
        'Без гаданий. С точкой фокуса.',
        reply_markup=one_button_keyboard(
            text='1299 ₽ / 2000 астробаллов',
            callback_data='buy_personal_report',
            back_button_data='vip_services',
        ),
    )


@router.callback_query(F.data == 'buy_personal_report')
async def buy_personal_report(query: CallbackQuery, state: FSMContext):
    await state.set_state(PersonalReportState.payment_type)
    await query.message.answer(
        'Выбери тип оплаты',
        reply_markup=get_payment_choices_kb(
            '2000 баллов',
            '1299 ₽',
        ),
    )


@router.callback_query(
    F.data.in_(('astropoints', 'money')),
    StateFilter(PersonalReportState.payment_type),
)
@flags.with_client
async def choose_personal_report_payment_type(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    if query.data == 'astropoints':
        if client.astropoints < 2000:
            await query.message.edit_text(
                astropoints_not_enough,
                reply_markup=get_payment_choices_kb(None, '1299 ₽'),
            )
            return
        client.astropoints -= 2000
        await client.asave()
        await query.message.edit_text(
            'Создаю отчет и аудио...\nЭто может занять несколько минут...',
        )
        await state.clear()
        await make_vip_report(query.message, client)
    else:
        await state.set_state(PersonalReportState.payment)
        await send_payment_link(
            query,
            state,
            amount=1299,
            description='Глубокий персональный отчёт',
            email=client.email,
        )


@router.callback_query(
    F.data == 'check_buying',
    StateFilter(PersonalReportState.payment),
)
@flags.with_client
async def on_successful_payment(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await check_payment(query, state)
    await Purchase.objects.from_client(
        client,
        PurchaseTypes.VIP_PERSONAL_REPORT,
    )
    await query.message.edit_text(
        'Создаю отчет и аудио...\nЭто может занять несколько минут...',
    )
    await state.clear()
    await make_vip_report(query.message, client)


#########################
### VIP COMPATABILITY ###
#########################


@router.callback_query(F.data == 'vip_compatibility')
@flags.with_client
async def vip_compatibility(callback: CallbackQuery, client: Client):
    await callback.message.edit_text(
        client.genderize(
            '❤️‍🔥 VIP-анализ совместимости\n\n'
            'Ты {gender:готов,готова} к настоящей глубине?\n'
            'Это больше, чем просто “подходите вы друг другу или нет”.\n'
            'Это разбор, после которого вы оба увидите себя иначе.\n\n'
            'Пара. Семья. Команда. Друзья.\n'
            'Выбирай формат — и ныряем вглубь.',
        ),
        reply_markup=one_button_keyboard(
            text='1599 ₽ / 2500 астробаллов',
            callback_data='buy_compatibility',
            back_button_data='vip_services',
        ),
    )


@router.callback_query(
    F.data.in_(('buy_compatibility', 'show_connection_depth')),
)
@flags.with_client
async def chose_payment_type(query: CallbackQuery, state: FSMContext):
    await state.set_state(VIPCompatabilityState.payment_type)
    await query.message.answer(
        'Выбери тип оплаты',
        reply_markup=get_payment_choices_kb(
            '2500 баллов',
            '1599 ₽',
        ),
    )


@router.callback_query(
    F.data.in_(('astropoints', 'money')),
    StateFilter(VIPCompatabilityState.payment_type),
)
@flags.with_client
async def buy_compatibility(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    if query.data == 'astropoints':
        if client.astropoints < 2500:
            await query.message.edit_text(
                astropoints_not_enough,
                reply_markup=get_payment_choices_kb(None, '1599 ₽'),
            )
            return
        client.astropoints -= 2500
        await client.asave()
        await query.message.edit_text(
            'Выбери тип связи, по которому ты хочешь получить совместимость',
            reply_markup=connection_types_kb,
        )
        await state.clear()
    else:
        await state.set_state(VIPCompatabilityState.payment)
        await send_payment_link(
            query,
            state,
            amount=1599,
            description='VIP-анализ совместимости',
            email=client.email,
        )


@router.callback_query(
    F.data == 'check_buying',
    StateFilter(VIPCompatabilityState.payment),
)
@router.callback_query(F.data == 'connection_types')
@flags.with_client
async def on_successful_vip_compatability_payment(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    await check_payment(query, state)
    await Purchase.objects.from_client(
        client,
        PurchaseTypes.VIP_COMPATABILITY,
    )
    await query.message.edit_text(
        text='Выбери тип связи',
        reply_markup=connection_types_kb,
    )
    await state.clear()


@router.callback_query(F.data.startswith('connection_type'))
async def connection_type_info(query: CallbackQuery, state: FSMContext):
    connection_type = query.data.split(':')[-1]
    await state.update_data(connection_type=connection_type)
    await query.message.edit_text(
        connection_types[connection_type],
        reply_markup=one_button_keyboard(
            text='Выбрать',
            callback_data='choose_connection_type',
            back_button_data='connection_types',
        ),
    )


@router.callback_query(F.data == 'choose_connection_type')
async def choose_connection_type(query: CallbackQuery):
    await query.message.edit_reply_markup(
        reply_markup=one_button_keyboard(
            text='Добавить человека',
            callback_data='add_person',
        ),
    )


@router.callback_query(F.data == 'add_person')
async def add_person(query: CallbackQuery, state: FSMContext):
    await state.set_state(VIPCompatabilityState.fullname)
    await query.message.answer('✍ Введи ФИО человека полностью')


@router.message(F.text, StateFilter(VIPCompatabilityState.fullname))
async def set_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullname=msg.text)
    await msg.answer('📆 Введи дату рождения человека в формате ДД.ММ.ГГГГ.')
    await state.set_state(VIPCompatabilityState.birth_date)


@router.message(F.text, StateFilter(VIPCompatabilityState.birth_date))
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
        '⏳ Введи точное время рождения человека. '
        'Это важно для точности разбора.\n'
        'Не знаешь? Выбери:',
        reply_markup=one_button_keyboard(
            text='Не знаю',
            callback_data='unknown_birth_time',
        ),
    )
    await state.set_state(VIPCompatabilityState.birth_time)


@router.message(F.text, StateFilter(VIPCompatabilityState.birth_time))
@router.callback_query(
    F.data.startswith('birth_time'),
    StateFilter(VIPCompatabilityState.birth_time),
)
async def set_birth_time(msg: Message | CallbackQuery, state: FSMContext):
    if isinstance(msg, Message):
        await validate_time(msg)
        birth_time = msg.text
        answer_func = msg.answer
    else:
        birth_time = msg.data.split('_')[-1]
        answer_func = msg.message.answer

    await state.update_data(birth_time=birth_time)
    await answer_func(
        'Отправь место рождения человека.\n📍 Только город — без страны',
    )
    await state.set_state(VIPCompatabilityState.birth_location)


@router.message(F.text, StateFilter(VIPCompatabilityState.birth_location))
async def set_birth_location(msg: Message, state: FSMContext):
    data = await state.get_data()
    birth = f'{data["birth_date"]} {data["birth_time"]}'
    birth = datetime.strptime(birth, settings.DATE_FMT).astimezone(
        settings.TZ,
    )
    async with HumanDesignAPI() as api:
        bodygraphs = await api.bodygraphs(
            HDInputData.from_datetime(birth, msg.text),
        )
    persons = data.get('persons', [])
    person = asdict(bodygraphs)
    person.update({'fullname': data['fullname']})
    persons.append(person)
    await state.update_data(persons=persons)
    await msg.answer(
        f'{data["fullname"]} добавлен',
        reply_markup=get_vip_compatability_report_kb(
            (data['connection_type'] == 'family' and len(persons) < 3)
            or (data['connection_type'] == 'team' and len(persons) < 2),
        ),
    )
    await state.set_state(VIPCompatabilityState.report)


@router.callback_query(
    F.data == 'vip_compatability_report',
    StateFilter(VIPCompatabilityState.report),
)
@flags.with_client
async def vip_compatability_report(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    data = await state.get_data()
    if data['connection_type'] == 'family' and len(data['persons']) < 2:
        await query.message.answer(
            'Для семьи надо ввести минимум трёх человек',
        )
        return

    await query.message.edit_text(
        'Создаю отчет и аудио...\nЭто может занять несколько минут...',
    )
    await state.set_state(None)

    person = asdict(Bodygraphs.from_client(client))
    person.update({'fullname': client.fullname})
    data['persons'].append(person)
    compatability = await SoulMuse().answer(
        get_vip_compatability_prompt(
            data['connection_type'],
            data['persons'],
        ),
    )

    await query.message.answer_document(
        BufferedInputFile(
            generate_pdf(compatability),
            'VIP-анализ совместимости.pdf',
        ),
    )
    await query.message.answer_audio(
        BufferedInputFile(
            await synthesize(compatability),
            'VIP-анализ совместимости.wav',
        ),
    )
