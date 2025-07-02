from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional

from aiogram import types
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import now

from core.choices import Actions, MonthTextTypes

if TYPE_CHECKING:
    from core.models import Client, FridayGift, MonthText, Payment


class ClientManager(models.Manager):
    async def from_tg_user(self, user: types.User) -> 'Client':
        return await self.acreate(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def update_from_tg_user(self, user: types.User) -> None:
        await self.filter(pk=user.id).aupdate(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def create_or_update_from_tg_user(
        self,
        user: types.User,
    ) -> tuple['Client', bool]:
        try:
            client = await self.aget(pk=user.id)
            await self.update_from_tg_user(user)
            await client.arefresh_from_db()
            return client, False
        except ObjectDoesNotExist:
            return await self.from_tg_user(user), True

    def annotate_actions(self, today: date):
        return self.annotate(
            universe_advice_count=models.Count(
                'actions',
                filter=models.Q(
                    actions__action=Actions.UNIVERSE_ADVICE,
                    actions__date__date=today,
                ),
            ),
            personal_day_count=models.Count(
                'actions',
                filter=models.Q(
                    actions__action=Actions.PERSONAL_DAY,
                    actions__date__date=today,
                ),
            ),
        )


class MonthTextManager(models.Manager):
    async def get_month_text(
        self,
        client: 'Client',
        type: MonthTextTypes,
    ) -> Optional['MonthText']:
        today = now()
        try:
            return await self.aget(
                client=client,
                created_at__month=today.month,
                created_at__year=today.year,
                type=type,
            )
        except ObjectDoesNotExist:
            return None


class FridayGiftManager(models.Manager):
    async def get_current_week_gift(
        self,
        client: 'Client',
    ) -> Optional['FridayGift']:
        today = now().date()
        first_week_day = today - timedelta(days=today.weekday())
        last_week_day = first_week_day + timedelta(days=6)
        try:
            return await self.filter(
                client=client,
                created_at__date__gte=first_week_day,
                created_at__date__lte=last_week_day,
            ).alatest('created_at')
        except ObjectDoesNotExist:
            return None

    async def get_latest_gift(
        self,
        client: 'Client',
    ) -> Optional['FridayGift']:
        try:
            return await self.filter(client=client).alatest('created_at')
        except ObjectDoesNotExist:
            return None


class PaymentManager(models.Manager):
    async def from_message(self, msg: types.Message) -> 'Payment':
        return await self.acreate(
            client_id=msg.chat.id,
            charge_id=msg.successful_payment.provider_payment_charge_id,
            payment_type=msg.successful_payment.invoice_payload,
        )
