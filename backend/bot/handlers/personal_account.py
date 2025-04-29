from datetime import datetime

from aiogram import F, Router, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline.personal_account import get_personal_account_kb
from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.settings import settings
from core.models import Client, FridayGift, Insight, SubscriptionPlans

router = Router()


@router.message(F.text == '👤 Soul Space')
@router.callback_query(F.data == 'soul_space')
@flags.with_client
async def personal_account_handler(
    msg: Message | CallbackQuery,
    client: Client,
):
    answers_func = (
        msg.answer if isinstance(msg, Message) else msg.message.edit_text
    )
    text = f'Астробаллы: {client.astropoints}\n'

    if client.subscription_end:
        sub_plan = SubscriptionPlans(client.subscription_plan)
        sub_end = datetime.strftime(
            client.subscription_end.astimezone(settings.TZ),
            settings.DATE_FMT,
        )
        text += (
            f'Подписка: {sub_plan.label}\nДата окончания подписки {sub_end}'
        )
        subscription_text = 'Продлить подписку'
    else:
        text += 'Вы еще не оформляли подписку'
        subscription_text = 'Оформить подписку'

    await answers_func(
        text,
        reply_markup=get_personal_account_kb(subscription_text),
    )


@router.callback_query(F.data == 'personal_gifts')
async def personal_gifts_handler(query: CallbackQuery):
    await query.message.edit_text(
        'Твои подарки',
        reply_markup=await keyboard_from_queryset(
            FridayGift,
            'friday_gift',
            str_func=lambda x: x.to_button_text(),
            back_button_data='soul_space',
        ),
    )


@router.callback_query(F.data.startswith('friday_gift'))
async def friday_gift_detail(query: CallbackQuery):
    gift = await FridayGift.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        gift.text,
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='personal_gifts',
        ),
    )


@router.callback_query(F.data == 'personal_insights')
async def personal_insights_handler(query: CallbackQuery, state: FSMContext):
    if audio_msg_id := await state.get_value('audio_msg_id'):
        try:
            await query.bot.delete_message(query.message.chat.id, audio_msg_id)
            await state.update_data(audio_msg_id=None)
        except TelegramBadRequest:
            pass

    await query.message.edit_text(
        'Твои инсайты',
        reply_markup=await keyboard_from_queryset(
            Insight,
            'insight',
            str_func=lambda x: x.to_button_text(),
            back_button_data='soul_space',
        ),
    )


@router.callback_query(F.data.startswith('insight'))
async def insight_detail(query: CallbackQuery, state: FSMContext):
    insight = await Insight.objects.aget(pk=query.data.split(':')[1])
    if insight.audio_file_id:
        await query.message.edit_text(
            'Вы можете прослушать свой инсайт',
            reply_markup=one_button_keyboard(
                text='Назад',
                callback_data='personal_insights',
            ),
        )
        audio_msg = await query.message.answer_audio(
            insight.audio_file_id,
            reply_markup=one_button_keyboard(
                text='Удалить',
                callback_data=f'delete_insight:{insight.pk}',
            ),
        )
        await state.update_data(audio_msg_id=audio_msg.message_id)
    else:
        await query.message.edit_text(
            insight.text,
            reply_markup=one_button_keyboard(
                text='Удалить',
                callback_data=f'delete_insight:{insight.pk}',
                back_button_data='personal_insights',
            ),
        )


@router.callback_query(F.data.startswith('delete_insight'))
async def delete_insight(query: CallbackQuery):
    await Insight.objects.filter(pk=query.data.split(':')[1]).adelete()
    if query.message.audio or query.message.voice:
        await query.message.delete()
    else:
        await query.message.edit_text(
            'Твои инсайты',
            reply_markup=await keyboard_from_queryset(
                Insight,
                'insight',
                str_func=lambda x: x.to_button_text(),
                back_button_data='soul_space',
            ),
        )
