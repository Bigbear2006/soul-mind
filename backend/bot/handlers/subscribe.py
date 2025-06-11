from datetime import datetime, timedelta

from aiogram import F, Router, flags
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from django.db import models

from bot.keyboards.utils import keyboard_from_choices, one_button_keyboard
from bot.loader import logger
from bot.settings import settings
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
        'trial_usages_ended'
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
    await state.update_data(
        subscription_plan=plan.value,
        back_button_data=None,
    )
    await query.message.edit_text(
        plan.teaser,
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


@router.pre_checkout_query(StateFilter(None))
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@router.message(F.successful_payment, StateFilter(None))
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
