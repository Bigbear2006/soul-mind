from typing import Optional

from aiogram import types
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from bot.loader import logger


class SubscriptionPlanChoices(models.TextChoices):
    STANDARD = 'standard', 'Стандартная'
    PREMIUM = 'premium', 'Премиум'

    @property
    def price(self):
        if self == SubscriptionPlanChoices.STANDARD:
            return 500
        elif self == SubscriptionPlanChoices.PREMIUM:
            return 1200
        else:
            raise ValueError('Invalid subscription plan')


class User(AbstractUser):
    pass


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


class Client(models.Model):
    id = models.PositiveBigIntegerField('Телеграм ID', primary_key=True)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField(
        'Фамилия',
        max_length=255,
        null=True,
        blank=True,
    )
    username = models.CharField('Ник', max_length=32, null=True, blank=True)
    is_premium = models.BooleanField('Есть премиум', default=False)
    invited_by = models.ForeignKey(
        'self',
        models.CASCADE,
        'invited_friends',
        verbose_name='Кем приглашен',
        null=True,
        blank=True,
    )
    astropoints = models.IntegerField('Астробаллы', default=0)
    subscription_plan = models.CharField(
        'Тип подписки',
        choices=SubscriptionPlanChoices,
        max_length=50,
        blank=True,
    )
    subscription_end = models.DateTimeField(
        verbose_name='Дата окончания подписки',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    objects = ClientManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        username = self.first_name
        if self.username:
            username += f' (@{self.username})'
        return username

    async def check_invitation(
        self,
        inviter_id: int | str,
    ) -> Optional['Client']:
        try:
            invited_by = await Client.objects.aget(pk=inviter_id)
        except ObjectDoesNotExist:
            logger.info(f'Invalid inviter_id - {inviter_id}')
            return

        self.invited_by = invited_by
        await self.asave()
        return invited_by
