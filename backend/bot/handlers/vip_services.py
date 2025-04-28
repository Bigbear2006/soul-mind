import asyncio
from dataclasses import asdict
from datetime import datetime

from aiogram import F, Router, flags
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from asgiref.sync import sync_to_async

from bot.api.humandesign import HumanDesignAPI
from bot.api.soul_muse import SoulMuse
from bot.api.speechkit import synthesize
from bot.keyboards.inline.registration import birth_times_kb
from bot.keyboards.inline.vip_services import (
    connection_types_kb,
    get_payment_choices_kb,
    get_topics_kb,
    get_vip_compatability_report_kb,
    vip_services_kb,
)
from bot.keyboards.utils import (
    keyboard_from_choices,
    one_button_keyboard,
)
from bot.loader import logger
from bot.pdf import generate_pdf
from bot.schemas import Bodygraphs, HDInputData
from bot.settings import settings
from bot.states import (
    MiniConsultState,
    PersonalReportState,
    VIPCompatabilityState,
)
from bot.templates.base import connection_types
from bot.templates.vip_services import (
    get_personal_report_prompt,
    get_vip_compatability_prompt,
)
from core.choices import (
    ExperienceTypes,
    ExpertTypes,
    FeelingsTypes,
    Intentions,
    MiniConsultFeedbackRatings,
)
from core.models import (
    Client,
    ExpertAnswer,
    MiniConsult,
    MiniConsultFeedback,
    MiniConsultTopic,
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


@router.pre_checkout_query(
    StateFilter(
        VIPCompatabilityState.payment,
        PersonalReportState.payment,
        MiniConsultState.payment,
    ),
)
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


####################
### MINI CONSULT ###
####################


@router.callback_query(F.data == 'vip_mini_consult')
async def vip_mini_consult(callback: CallbackQuery):
    await callback.message.edit_text(
        '🎧 Мини-консультация с экспертом\n\n'
        'У тебя есть вопрос, и он требует живого голоса.\n'
        'Астролог. Нумеролог. Эксперт по Хьюман-дизайну. '
        'Психолог. Духовный наставник-энергопрактик.\n\n'
        '3–5 голосовых от того, кто умеет читать глубже.',
        reply_markup=one_button_keyboard(
            text='✨ Задать вопрос эксперту – 999 ₽ / 1500 баллов',
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
            '1500 баллов',
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
            await query.message.answer('Не хватает астробаллов')
            return
        client.astropoints -= 1500
        await client.asave()
        await query.message.edit_text(
            'Выбери тип эксперта',
            reply_markup=keyboard_from_choices(ExpertTypes, prefix='expert'),
        )
        await state.clear()
    else:
        await query.message.answer_invoice(
            'Мини-консультация с экспертом',
            'Мини-консультация с экспертом',
            'mini_consult',
            settings.CURRENCY,
            [LabeledPrice(label=settings.CURRENCY, amount=999 * 100)],
            settings.PROVIDER_TOKEN,
        )
        await state.set_state(MiniConsultState.payment)


@router.message(
    F.successful_payment,
    StateFilter(MiniConsultState.payment),
)
@flags.with_client
async def choose_expert_type(msg: Message):
    await msg.answer(
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
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.answer
    )
    intention = (
        msg.text if isinstance(msg, Message) else msg.data.split(':')[1]
    )
    await state.update_data(intention=intention)
    await answer_func(
        'Ты уже сталкивался с этим направлением?',
        reply_markup=keyboard_from_choices(
            ExperienceTypes, prefix='experience',
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
async def choose_topics(query: CallbackQuery, state: FSMContext):
    await state.update_data(feelings_type=query.data.split(':')[1])
    await state.set_state(MiniConsultState.topics)
    await query.message.edit_text(
        'Выбери до трех меток, к которым относится твой вопрос.\n'
        'Если нужно метки нет в списке, то можешь написать ее.',
        reply_markup=await get_topics_kb(),
    )


@router.message(F.text, StateFilter(MiniConsultState.topics))
@router.callback_query(
    F.data.startswith('topic'),
    StateFilter(MiniConsultState.topics),
)
async def ask_question(msg: Message | CallbackQuery, state: FSMContext):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.answer
    )

    pk = msg.data.split(':')[1] if isinstance(msg, CallbackQuery) else ''
    topics = await state.get_value('topics', [])
    if pk != 'done' or len(topics) == 3:
        if isinstance(msg, Message):
            topic, created = await Topic.objects.aget_or_create(name=msg.text)
        else:
            topic = await Topic.objects.aget(pk=pk)
        topics.append(topic.pk)
        await state.update_data(topics=topics)
        await answer_func(f'Метка {topic} добавлена')

    if pk == 'done' or len(topics) == 3:
        await state.set_state(MiniConsultState.question)
        await answer_func(
            '— «Вопрос — это не просто слова. Это как зеркало. Чем яснее ты сформулируешь, '
            'тем точнее голос найдёт путь. Вот три подсказки от меня...»\n'
            '1. Будь конкретен. Вместо «что мне делать?» скажи: '
            '«я застрял в отношениях и не понимаю, это страх или правда?»\n'
            '2. Говори голосом, если можешь. В твоей интонации больше правды, чем ты думаешь.\n'
            '3. Если не знаешь, как спросить — просто скажи это. Это уже начало. И это нормально.\n'
            'Soul Muse — не судит. Она слышит. И помогает видеть, что внутри уже есть ответ.',
        )


@router.message(F.text | F.voice, StateFilter(MiniConsultState.question))
@flags.with_client
async def send_question_to_expert(
    msg: Message, state: FSMContext, client: Client,
):
    data = await state.get_data()
    topics_ids = data['topics']
    consult = await MiniConsult.objects.acreate(
        client=client,
        text=msg.text or '',
        audio_file_id=msg.voice.file_id if msg.voice else None,
        expert_type=data['expert_type'],
        intention=data['intention'],
        experience_type=data['experience_type'],
        feelings_type=data['feelings_type'],
    )
    await MiniConsultTopic.objects.abulk_create(
        [MiniConsultTopic(consult=consult, topic_id=t) for t in topics_ids],
    )
    topics = await sync_to_async(
        lambda: list(
            Topic.objects.filter(pk__in=topics_ids).values_list(
                'name', flat=True,
            )
        ),
    )()

    text = (
        f'Пользователь: {client}\n'
        f'Тип эксперта: {ExpertTypes(data["expert_type"]).label}\n'
        f'Намерение: {Intentions(data["intention"]).label}\n'
        f'Уже сталкивался: {ExperienceTypes(data["experience_type"]).label}\n'
        f'Ощущения: {FeelingsTypes(data["feelings_type"]).label}\n'
        f'Метки: {", ".join(topics)}'
    )
    kb = one_button_keyboard(
        text='Ответить', callback_data=f'answer_consult:{consult.pk}',
    )

    if msg.voice:
        await msg.bot.send_audio(
            settings.EXPERTS_CHAT_ID,
            msg.voice.file_id,
            caption=text,
            reply_markup=kb,
        )
    else:
        text += f'\n\nВопрос:\n{msg.text}'
        await msg.bot.send_message(
            settings.EXPERTS_CHAT_ID,
            text,
            reply_markup=kb,
        )

    await msg.answer('Вопрос принят. Эксперт ответит в течение 24 часов.')
    await state.clear()


@router.callback_query(
    F.data.startswith('answer_consult'),
    F.message.chat.id == settings.EXPERTS_CHAT_ID,
)
async def answer_consult(query: CallbackQuery, state: FSMContext):
    consult_id = query.data.split(':')[1]
    await state.update_data(consult_id=consult_id)
    await state.set_state(MiniConsultState.answer_consult)
    await query.message.reply(
        'Запишите несколько голосовых сообщений',
        reply_markup=one_button_keyboard(
            text='Завершить консультацию',
            callback_data=f'end_consult:{consult_id}',
        ),
    )


@router.message(
    F.voice,
    F.chat.id == settings.EXPERTS_CHAT_ID,
    StateFilter(MiniConsultState.answer_consult),
)
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
    F.message.chat.id == settings.EXPERTS_CHAT_ID,
)
async def end_consult(query: CallbackQuery, state: FSMContext):
    consult = await MiniConsult.objects.select_related('client').aget(
        pk=await state.get_value('consult_id'),
    )
    answers = ExpertAnswer.objects.filter(consult=consult)

    async for answer in answers:
        await query.bot.send_audio(
            consult.client.pk, audio=answer.audio_file_id,
        )
        await asyncio.sleep(1)

    await query.bot.send_message(
        consult.client.pk,
        'Как тебе консультация?',
        reply_markup=keyboard_from_choices(
            MiniConsultFeedbackRatings,
            prefix=f'feedback:{consult.pk}',
        ),
    )

    await query.message.edit_text('Консультация завершена')


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


@router.callback_query(
    F.data == 'send_feedback_without_comment',
    StateFilter(MiniConsultState.comment),
)
async def send_feedback_without_comment(
    query: CallbackQuery, state: FSMContext,
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
    await MiniConsultFeedback.objects.acreate(
        consult_id=data['consult_id'],
        rating=data['rating'],
        audio_file_id=msg.voice.file_id if msg.voice else None,
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
        'PDF + голос Soul Muse.\n'
        'Без гаданий. С точкой фокуса.',
        reply_markup=one_button_keyboard(
            text='🌀 Получить отчёт – 1299 ₽ / 2000 баллов',
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
            await query.message.answer('Не хватает астробаллов')
            return
        client.astropoints -= 2000
        await client.asave()
        await query.message.edit_text(
            'Создаю отчет и аудио...\nЭто может занять несколько минут...',
        )
        await state.clear()
    else:
        await query.message.answer_invoice(
            'Глубокий персональный отчёт',
            'Глубокий персональный отчёт',
            'personal_report',
            settings.CURRENCY,
            [LabeledPrice(label=settings.CURRENCY, amount=1299 * 100)],
            settings.PROVIDER_TOKEN,
        )
        await state.set_state(VIPCompatabilityState.payment)


@router.message(
    F.successful_payment,
    StateFilter(PersonalReportState.payment),
)
@flags.with_client
async def on_successful_payment(
    msg: Message,
    state: FSMContext,
    client: Client,
):
    await msg.answer(
        'Создаю отчет и аудио...\nЭто может занять несколько минут...',
    )
    await state.clear()
    report = await SoulMuse().answer(get_personal_report_prompt())
    await msg.answer_document(
        BufferedInputFile(generate_pdf(report), 'personal_report.pdf'),
    )
    # await msg.answer_audio(
    #     BufferedInputFile(await synthesize(report), 'personal_report.wav'),
    # )
    await state.clear()


#########################
### VIP COMPATABILITY ###
#########################


@router.callback_query(F.data == 'vip_compatibility')
async def vip_compatibility(callback: CallbackQuery):
    await callback.message.edit_text(
        '❤️‍🔥 VIP-анализ совместимости\n\n'
        'Ты готов(а) к настоящей глубине?\n'
        'Это больше, чем просто “подходите вы друг другу или нет”.\n'
        'Это разбор, после которого вы оба увидите себя иначе.\n\n'
        'Пара. Семья. Команда. Друзья.\n'
        'Выбирай формат — и ныряем вглубь.',
        reply_markup=one_button_keyboard(
            text='💎 Узнать глубину связи – 1599 ₽ / 2500 баллов',
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
            await query.message.answer('Не хватает астробаллов')
            return
        client.astropoints -= 2500
        await client.asave()
        await query.message.edit_text(
            'Выбери тип связи',
            reply_markup=connection_types_kb,
        )
        await state.clear()
    else:
        await query.message.answer_invoice(
            'VIP-анализ совместимости',
            'VIP-анализ совместимости',
            'vip_compatability',
            settings.CURRENCY,
            [LabeledPrice(label=settings.CURRENCY, amount=1599 * 100)],
            settings.PROVIDER_TOKEN,
        )
        await state.set_state(VIPCompatabilityState.payment)


@router.message(
    F.successful_payment,
    StateFilter(VIPCompatabilityState.payment),
)
@router.callback_query(F.data == 'connection_types')
async def on_successful_vip_compatability_payment(
    msg: Message | CallbackQuery,
    state: FSMContext,
):
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    await answer_func('Выбери тип связи', reply_markup=connection_types_kb)
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
        reply_markup=birth_times_kb,
    )
    await state.set_state(VIPCompatabilityState.birth_time)


@router.message(F.text, StateFilter(VIPCompatabilityState.birth_time))
@router.callback_query(
    F.data.startswith('birth_time'),
    StateFilter(VIPCompatabilityState.birth_time),
)
async def set_birth_time(msg: Message | CallbackQuery, state: FSMContext):
    if isinstance(msg, Message):
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
    person = asdict(Bodygraphs.from_client(client))
    person.update({'fullname': client.fullname})
    data['persons'].append(person)
    compatability = await SoulMuse().answer(
        get_vip_compatability_prompt(
            data['connection_type'],
            data['persons'],
        ),
    )

    await query.message.edit_text(
        'Создаю отчет и аудио...\nЭто может занять несколько минут...',
    )
    await state.clear()

    await query.message.answer_document(
        BufferedInputFile(
            generate_pdf(compatability),
            'vip_compatability.pdf',
        ),
    )
    # await query.message.answer_audio(
    #     BufferedInputFile(
    #         await synthesize(compatability),
    #         'vip_compatability.wav',
    #     ),
    # )
