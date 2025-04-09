from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from django.db import models

from bot.keyboards.inline import keyboard_from_choices
from bot.keyboards.utils import one_button_keyboard
from bot.loader import logger
from bot.settings import settings
from core.models import Client, SubscriptionPlans

router = Router()


@router.callback_query(F.data == 'subscription_plans')
async def subscription_plans_handler(query: CallbackQuery):
    await query.message.edit_text(
        'Выберите тип подписки',
        reply_markup=keyboard_from_choices(SubscriptionPlans),
    )


@router.callback_query(F.data.in_(SubscriptionPlans.values))
async def choose_subscription_plan(query: CallbackQuery, state: FSMContext):
    plan = SubscriptionPlans(query.data)
    await state.update_data(subscription_plan=plan.value)
    await query.message.edit_text(
        f'{plan.label} - {plan.price} ₽',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data='pay_subscription',
            back_button_data='subscription_plans',
        ),
    )


@router.callback_query(F.data == 'pay_subscription')
async def subscribe_handler(query: CallbackQuery, state: FSMContext):
    plan = SubscriptionPlans(
        await state.get_value('subscription_plan'),
    )
    await query.message.answer_invoice(
        f'Оплата подписки {plan.label}',
        f'Оплата подписки {plan.label}',
        plan.value,
        settings.CURRENCY,
        [LabeledPrice(label=settings.CURRENCY, amount=plan.price * 100)],
        settings.PROVIDER_TOKEN,
    )


@router.pre_checkout_query()
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@router.message(F.successful_payment)
async def on_successful_payment(msg: Message, state: FSMContext):
    client = await Client.objects.prefetch_related('invited_by').aget(
        pk=msg.chat.id,
    )
    plan = SubscriptionPlans(
        await state.get_value('subscription_plan'),
    )

    first_subscription = not client.subscription_end
    subscription_end = (
        client.subscription_end
        if client.subscription_end
        else datetime.now(settings.TZ)
    )
    await Client.objects.filter(pk=msg.chat.id).aupdate(
        subscription_end=subscription_end + timedelta(days=30),
        subscription_plan=plan.value,
    )

    if first_subscription and client.invited_by:
        await Client.objects.filter(pk=client.invited_by.pk).aupdate(
            astropoints=models.F('astropoints') + 150,
        )

        try:
            await msg.bot.send_message(
                client.invited_by.pk,
                f'Пользователь {client} перешел по вашей реферальной ссылке '
                f'и оформил подписку "{plan.label}".\n'
                f'Вам начислено 150 астробаллов',
            )
        except TelegramAPIError as e:
            logger.info(
                f'Send message (+150 astropoints) error '
                f'{e.__class__.__name__}: {e}',
            )

    await msg.answer(f'Вы оплатили подписку "{plan.label}" на 30 дней')
    await state.clear()
