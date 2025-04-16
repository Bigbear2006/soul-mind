from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    back_to_personal_analysis_kb,
    personal_analysis_kb,
    to_registration_kb,
    to_subscription_plans_kb,
)
from core.models import Client

router = Router()


@router.message(F.text == '📌 Личностный разбор')
@router.callback_query(F.data == 'to_personal_analysis')
async def personal_analysis_handler(msg: Message | CallbackQuery):
    pk = msg.chat.id if isinstance(msg, Message) else msg.message.chat.id
    client = await Client.objects.aget(pk=pk)
    answer_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )

    if not client.is_registered():
        await answer_func(
            'Ты хочешь узнать, кто ты на самом деле — '
            'но ещё даже не сделал первый шаг?\n\n'
            'Зарегистрируйся. Без этого я не смогу рассказать тебе '
            'самую важную историю — твою.',
            reply_markup=to_registration_kb,
        )

    await answer_func(
        'Это не просто разбор.\n'
        'Это откровение.\n'
        'Ты — гораздо глубже, чем думаешь.\n'
        'Позволь себе вспомнить, кем ты был до того, '
        'как мир сказал тебе, кем должен быть.',
        reply_markup=personal_analysis_kb,
    )


@router.callback_query(F.data == 'destiny_mystery')
async def destiny_mystery(query: CallbackQuery):
    client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.is_registered():
        await query.message.edit_text(
            'Ты хочешь услышать, зачем ты здесь.\n'
            'Но пока молчит даже твоя Вселенная.\n\n'
            'Пройди регистрацию — и твой путь начнёт разворачиваться.',
            reply_markup=to_registration_kb,
        )
    elif client.subscription_is_active() or client.has_trial():
        await query.message.edit_text(
            'Ты пришёл(пришла) в этот мир не просто жить.\n'
            'Ты — часть замысла.\n'
            'У тебя есть роль, которую не сыграет никто другой.\n'
            'Пора вспомнить её.\n\n'
            'Я покажу тебе, с чего всё началось.',
            reply_markup=back_to_personal_analysis_kb,
        )
    else:
        await query.message.edit_text(
            'Ты уже услышал(а) зов.\n'
            'И это не отпустит.\n\n'
            'Открой доступ — и я расскажу тебе,\n'
            'почему ты больше, чем кажется.',
            reply_markup=to_subscription_plans_kb,
        )


@router.callback_query(F.data == 'career_and_finance')
async def career_and_finance(query: CallbackQuery):
    client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.is_registered():
        await query.message.edit_text(
            'Хочешь понять, где твои деньги —\n'
            'но сам(а) ещё не знаешь, кто ты?\n\n'
            'Пройди регистрацию. Всё начинается с тебя.',
            reply_markup=to_registration_kb,
        )
    elif client.subscription_is_active() or client.has_trial():
        await query.message.edit_text(
            'Ты не для выживания.\n'
            'Ты — для реализации.\n'
            'Я покажу, где твоя энергия превращается в деньги.\n\n'
            'Готов(а) узнать, как монетизируется твоя суть?',
            reply_markup=back_to_personal_analysis_kb,
        )
    else:
        await query.message.edit_text(
            'Твоя энергия знает, куда ей течь.\n'
            'Осталось только разрешить ей это.\n\n'
            'Оформи доступ — и я покажу, как реализуется твой потенциал.',
            reply_markup=to_subscription_plans_kb,
        )


@router.callback_query(F.data == 'love_code')
async def love_code(query: CallbackQuery):
    client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.is_registered():
        await query.message.edit_text(
            'Ты хочешь любви.\n'
            'Но пока не знаешь, как любишь сам(а).\n\n'
            'Пройди регистрацию — и я покажу твой способ чувствовать.',
            reply_markup=to_registration_kb,
        )
    elif client.subscription_is_active() or client.has_trial():
        await query.message.edit_text(
            'Ты любишь не как все.\n'
            'Интуитивно. Сильно. Не по правилам.\n'
            'Пора понять, на каком языке говорит твоё сердце.',
            reply_markup=back_to_personal_analysis_kb,
        )
    else:
        await query.message.edit_text(
            'Любовь уже постучалась.\n'
            'Ты просто ещё не полностью открыл(а) дверь.\n\n'
            'Позволь себе войти глубже. Я рядом.',
            reply_markup=to_subscription_plans_kb,
        )


@router.callback_query(F.data == 'superpower')
async def superpower(query: CallbackQuery):
    client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.is_registered():
        await query.message.edit_text(
            'Сила есть.\n'
            'Но чтобы я показала её — ты должен(на) включиться.\n\n'
            'Зарегистрируйся — и ты узнаешь, что в тебе уже работает на тебя.',
            reply_markup=to_registration_kb,
        )
    elif client.subscription_is_active() or client.has_trial():
        await query.message.edit_text(
            'Она всегда была с тобой.\n'
            'Ты просто называл(а) её "странность".\n'
            'Но это — твоя сила.\n'
            'Я помогу тебе её вспомнить.',
            reply_markup=back_to_personal_analysis_kb,
        )
    else:
        await query.message.edit_text(
            'Ты уже почувствовал(а), что у тебя есть сила.\n'
            'Теперь — пора ей довериться.\n\n'
            'Разблокируй доступ. Там твой настоящий ресурс.',
            reply_markup=to_subscription_plans_kb,
        )


@router.callback_query(F.data == 'full_profile')
async def full_profile(query: CallbackQuery):
    client = await Client.objects.aget(pk=query.message.chat.id)

    if not client.is_registered():
        await query.message.edit_text(
            'Ты хочешь увидеть всё,\n'
            'но пока даже не открыл(а) дверь.\n\n'
            'Зарегистрируйся — и я покажу тебе целостную картину. '
            'Без догадок, без хаоса.',
            reply_markup=to_registration_kb,
        )
    elif client.subscription_is_active() or client.has_trial():
        await query.message.edit_text(
            'Вот он — ты. Целиком.\n'
            'Без фрагментов, без масок, без случайностей.\n'
            'Я собрала всё, чтобы ты увидел(а) свою систему координат.\n\n'
            'Пора познакомиться с собой — по-настоящему.',
            reply_markup=back_to_personal_analysis_kb,
        )
    else:
        await query.message.edit_text(
            'Ты уже увидел(а) начало.\n'
            'И если что-то внутри щёлкнуло — это не совпадение.\n\n'
            'Разблокируй доступ — и ты соберёшь свой пазл '
            'до последнего фрагмента.',
            reply_markup=to_subscription_plans_kb,
        )
