from dataclasses import asdict
from datetime import datetime
from io import BytesIO

from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery, BufferedInputFile,
)
from fpdf import FPDF

from bot.api.humandesign import HumanDesignAPI
from bot.api.soul_muse import SoulMuse
from bot.keyboards.inline import (
    birth_times_kb,
    connection_types_kb,
    get_vip_compatability_report_kb,
    vip_compatibility_payment_choices_kb,
    vip_services_kb,
)
from bot.keyboards.utils import one_button_keyboard
from bot.schemas import Bodygraphs, HDInputData
from bot.settings import settings
from bot.states import VIPCompatabilityState
from bot.templates.base import connection_types
from bot.templates.vip_services import get_vip_compatability_prompt
from core.models import Client

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
        'Выбери тип оплаты', reply_markup=vip_compatibility_payment_choices_kb,
    )


@router.callback_query(
    F.data.in_(('astropoints', 'money')),
    StateFilter(VIPCompatabilityState.payment_type),
)
@flags.with_client
async def buy_compatibility(
    query: CallbackQuery, state: FSMContext, client: Client,
):
    if query.data == 'astropoints':
        if client.astropoints < 2500:
            await query.message.answer('Не хватает астробаллов')
            return
        client.astropoints -= 2500
        await client.asave()
        await query.message.edit_text(
            'Выбери тип связи', reply_markup=connection_types_kb,
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


@router.pre_checkout_query(StateFilter(VIPCompatabilityState.payment))
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@router.message(
    F.successful_payment, StateFilter(VIPCompatabilityState.payment),
)
@router.callback_query(F.data == 'connection_types')
async def on_successful_payment(
    msg: Message | CallbackQuery, state: FSMContext,
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
        'Отправь место рождения человека.\n'
        '📍 Только город — без страны',
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


@router.callback_query(F.data == 'vip_compatability_report', StateFilter(VIPCompatabilityState.report))
@flags.with_client
async def vip_compatability_report(
    query: CallbackQuery, state: FSMContext, client: Client,
):
    data = await state.get_data()
    person = asdict(Bodygraphs.from_client(client))
    person.update({'fullname': client.fullname})
    data['persons'].append(person)
    compatability = await SoulMuse().get_vip_compatability(
        data['connection_type'],
        data['persons'],
    )
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Arial', '', 'assets/arial.ttf', uni=True)
    pdf.set_font("Arial", size=14)
    pdf.multi_cell(0, 10, text=compatability)
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    await query.message.answer_document(
        BufferedInputFile(
            pdf_bytes.getvalue(),
            'vip_compatability.pdf'
        )
    )
    await state.clear()
