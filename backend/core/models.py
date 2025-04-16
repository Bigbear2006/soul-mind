from datetime import datetime, timedelta
from typing import Optional

from aiogram import types
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from bot.loader import logger
from bot.settings import settings


class SubscriptionPlans(models.TextChoices):
    STANDARD = 'standard', 'Стандартная'
    PREMIUM = 'premium', 'Премиум'

    @property
    def price(self):
        if self == SubscriptionPlans.STANDARD:
            return 500
        elif self == SubscriptionPlans.PREMIUM:
            return 1200
        else:
            raise ValueError('Invalid subscription plan')


class Genders(models.TextChoices):
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


class QuestStatuses(models.TextChoices):
    COMPLETED = 'completed', 'Выполнен'
    SKIPPED = 'skipped', 'Пропущен'


class Actions(models.TextChoices):
    YOUR_COMPATABILITY_ENERGY = (
        'your_compatability_energy',
        'Энергия вашей совместимости',
    )
    SOUL_MUSE_QUESTION = 'soul_muse_question', 'Спроси у Soul Muse'
    FRIDAY_GIFT = 'friday_gift', 'Пятничный подарок'


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
        choices=SubscriptionPlans,
        max_length=50,
        blank=True,
    )
    subscription_end: datetime = models.DateTimeField(
        verbose_name='Дата окончания подписки',
        null=True,
        blank=True,
    )
    gender = models.CharField(
        'Пол',
        choices=Genders,
        max_length=50,
        blank=True,
    )
    fullname = models.CharField('ФИО', max_length=255, blank=True)
    birth = models.DateTimeField(
        'Дата и время рождения',
        null=True,
        blank=True,
    )
    birth_latitude = models.FloatField('Широта', null=True)
    birth_longitude = models.FloatField('Долгота', null=True)
    notifications_enabled = models.BooleanField('Уведомления', default=False)
    created_at: datetime = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
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

    def has_trial(self) -> bool:
        return self.created_at + timedelta(days=3) > datetime.now(settings.TZ)

    def subscription_is_active(self) -> bool:
        if self.subscription_end:
            return self.subscription_end > datetime.now(settings.TZ)
        return False

    def is_registered(self) -> bool:
        return self.birth_longitude is not None

    def get_action_permission(self, action: Actions) -> bool:
        if self.subscription_is_active():
            return True
        return False


class DailyQuest(models.Model):
    text = models.TextField('Задание')
    objects: models.Manager

    class Meta:
        verbose_name = 'Ежедневный квест'
        verbose_name_plural = 'Ежедневные квесты'

    def __str__(self):
        return self.text[:50]


class ClientDailyQuest(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'daily_quests',
        verbose_name='Пользователь',
    )
    quest = models.ForeignKey(
        DailyQuest,
        models.CASCADE,
        'clients',
        verbose_name='Квест',
    )
    status = models.CharField(
        'Статус',
        choices=QuestStatuses,
        max_length=50,
        blank=True,
    )
    created_at = models.DateTimeField('Дата прохождения', auto_now_add=True)
    objects: models.Manager

    class Meta:
        verbose_name = 'Результат ежедневного квеста'
        verbose_name_plural = 'Результаты ежедневных квестов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.quest}'


class WeeklyQuest(models.Model):
    title = models.TextField('Название')
    objects: models.Manager

    class Meta:
        verbose_name = 'Еженедельный квест'
        verbose_name_plural = 'Еженедельные квесты'

    def __str__(self):
        return self.title[:50]


class WeeklyQuestTask(models.Model):
    quest = models.ForeignKey(
        WeeklyQuest,
        models.CASCADE,
        'tasks',
        verbose_name='Квест',
    )
    day = models.IntegerField(
        'День',
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        default=1,
    )
    text = models.TextField('Задание')
    objects: models.Manager

    def __str__(self):
        return f'[{self.day} день] {self.quest}'

    class Meta:
        unique_together = ('quest', 'day')
        verbose_name = 'Задача еженедельного квеста'
        verbose_name_plural = 'Задачи еженедельных квестов'


class ClientWeeklyQuest(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'weekly_quests',
        verbose_name='Пользователь',
    )
    quest = models.ForeignKey(
        WeeklyQuest,
        models.CASCADE,
        'clients',
        verbose_name='Квест',
    )
    date = models.DateTimeField('Дата записи', auto_now_add=True)
    objects: models.Manager

    class Meta:
        unique_together = ('client', 'quest')
        verbose_name = 'Запись на еженедельный квест'
        verbose_name_plural = 'Записи на еженедельные квесты'
        ordering = ['-date']

    def __str__(self):
        return f'{self.client} - {self.quest}'


class ClientWeeklyQuestTask(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'weekly_quests_tasks',
        verbose_name='Пользователь',
    )
    quest = models.ForeignKey(
        WeeklyQuestTask,
        models.CASCADE,
        'clients',
        verbose_name='Квест',
    )
    status = models.CharField(
        'Статус',
        choices=QuestStatuses,
        max_length=50,
        blank=True,
    )
    created_at = models.DateTimeField('Дата прохождения', auto_now_add=True)
    objects: models.Manager

    class Meta:
        unique_together = ('client', 'quest')
        verbose_name = 'Результат еженедельного квеста'
        verbose_name_plural = 'Результаты еженедельных квестов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.quest}'


class ClientAction(models.Model):
    client = models.ForeignKey(Client, models.CASCADE, 'actions')
    action = models.CharField('Действие', max_length=100, choices=Actions)
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Действие пользователя'
        verbose_name_plural = 'Действия пользователей'
        ordering = ['-date']

    def __str__(self):
        return f'{self.client} - {Actions(self.action).label}'
