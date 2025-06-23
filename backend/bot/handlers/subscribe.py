from datetime import datetime, timedelta

from aiogram import F, Router, flags
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
)
from django.db import models

from bot.keyboards.inline.subscribe import get_subscription_plan_kb
from bot.keyboards.utils import keyboard_from_choices
from bot.loader import logger
from bot.services.payment import check_payment, send_payment_link
from bot.settings import settings
from bot.utils.formatters import months_plural
from core.models import Client, SubscriptionPlans

router = Router()


@router.callback_query(F.data == 'subscription_plans')
@router.callback_query(F.data == 'subscription_plans_with_back_button')
@flags.with_client
async def subscription_plans_handler(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    back_button_data = (
        'compatability_energy'
        if query.data == 'subscription_plans_with_back_button'
        else None
    )
    await state.set_state()
    await query.message.edit_text(
        client.genderize(SubscriptionPlans.subscription_plans_teaser()),
        reply_markup=keyboard_from_choices(
            SubscriptionPlans,
            back_button_data=back_button_data,
        ),
    )


@router.callback_query(F.data.in_(SubscriptionPlans.values))
async def choose_subscription_plan(query: CallbackQuery, state: FSMContext):
    plan = SubscriptionPlans(query.data)
    await state.update_data(subscription_plan=plan.value)
    await query.message.edit_text(
        plan.teaser,
        reply_markup=get_subscription_plan_kb(plan),
    )


@router.callback_query(F.data.startswith('pay_subscription'))
@flags.with_client
async def subscribe_handler(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    plan = SubscriptionPlans(
        await state.get_value('subscription_plan'),
    )
    months = int(query.data.split(':')[1])
    amount = plan.price if months == 1 else plan.price * 8

    await state.update_data(months=months)
    await send_payment_link(
        query,
        state,
        amount=amount,
        description=f'Оплата подписки {plan.label} на ({months} {months_plural(months)})',
        email=client.email,
    )


@router.callback_query(F.data == 'check_buying', StateFilter(None))
async def on_successful_payment(query: CallbackQuery, state: FSMContext):
    await check_payment(query, state)

    data = await state.get_data()
    client = await Client.objects.prefetch_related('invited_by').aget(
        pk=query.message.chat.id,
    )
    plan = SubscriptionPlans(data['subscription_plan'])

    first_subscription = not client.subscription_end
    subscription_end = (
        client.subscription_end
        if client.subscription_end
        else datetime.now(settings.TZ)
    )
    days = 30 if data['months'] == 1 else 365
    await Client.objects.filter(pk=client.pk).aupdate(
        subscription_end=subscription_end + timedelta(days=days),
        subscription_plan=plan.value,
    )

    if first_subscription and client.invited_by:
        await Client.objects.filter(pk=client.invited_by.pk).aupdate(
            astropoints=models.F('astropoints') + 150,
        )

        try:
            await query.bot.send_message(
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

    await query.message.edit_text(
        f'Вы оплатили подписку "{plan.label}" на {days} дней',
    )
    await state.clear()


@router.callback_query(F.data == 'cancel_buying')
async def cancel_subscription_buying(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text('Платеж отменен')
