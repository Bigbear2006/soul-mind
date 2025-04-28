from datetime import datetime, timedelta
from typing import Optional

from aiogram import types
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from bot.loader import logger
from bot.settings import settings
from core.choices import (
    Actions,
    ExperienceTypes,
    ExpertTypes,
    FeelingsTypes,
    FridayGiftTypes,
    Genders,
    Intentions,
    MiniConsultFeedbackRatings,
    MonthTextTypes,
    QuestStatuses,
    SubscriptionPlans,
)


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


class MonthTextManager(models.Manager):
    async def get_month_text(
        self,
        client: 'Client',
        type: MonthTextTypes,
    ) -> Optional['MonthText']:
        try:
            return await self.aget(
                client=client,
                created_at__month=now().month,
                type=type,
            )
        except ObjectDoesNotExist:
            return None


class FridayGiftManager(models.Manager):
    async def get_current_week_gift(
        self,
        client: 'Client',
    ) -> Optional['FridayGift']:
        today = now()
        first_week_day = today - timedelta(days=today.weekday())
        first_week_day = first_week_day.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        last_week_day = first_week_day + timedelta(days=6)
        last_week_day = last_week_day.replace(hour=23, minute=59, second=59)
        try:
            return await self.aget(
                client=client,
                created_at__gte=first_week_day,
                created_at__lte=last_week_day,
            )
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
    tzone = models.FloatField('Часовой пояс', null=True)
    type = models.CharField('Тип', max_length=255, blank=True)
    profile = models.CharField('Профиль', max_length=255, blank=True)
    centers = ArrayField(
        models.CharField(max_length=50),
        verbose_name='Центры',
        default=list,
        null=True,
        blank=True,
    )
    strategy = models.CharField('Стратегия', max_length=255, blank=True)
    authority = models.CharField('Авторитет', max_length=255, blank=True)
    gates = ArrayField(
        models.CharField(max_length=50),
        verbose_name='Ворота',
        default=list,
        null=True,
        blank=True,
    )
    definition = models.CharField('Определение', max_length=255, blank=True)
    channels_long = ArrayField(
        models.CharField(max_length=150),
        verbose_name='Каналы',
        default=list,
        null=True,
        blank=True,
    )
    planets = models.JSONField(
        verbose_name='Планеты',
        default=list,
        null=True,
        blank=True,
    )
    houses = models.JSONField(
        verbose_name='Дома',
        default=list,
        null=True,
        blank=True,
    )
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
        return self.houses is not None

    async def get_remaining_usages(self, action: Actions) -> int:
        usages = await ClientAction.objects.filter(
            client=self,
            action=action,
            date__month=now().month,
        ).acount()

        purchased = (
            await ClientActionBuying.objects.filter(
                client=self,
                action=action,
            ).aaggregate(total_count=models.Sum('count', default=0))
        )['total_count']

        if action == Actions.COMPATABILITY_ENERGY:
            if self.subscription_is_active():
                if self.subscription_plan == SubscriptionPlans.PREMIUM:
                    return 1  # unlimited
                else:
                    return 3 - usages + purchased
            elif self.has_trial():
                return 2 - usages + purchased
            else:
                return 0

        elif action == Actions.SOUL_MUSE_QUESTION:
            if self.subscription_is_active():
                if self.subscription_plan == SubscriptionPlans.PREMIUM:
                    return 15 - usages + purchased
                else:
                    return 4 - usages + purchased
            elif self.has_trial():
                return 2 - usages + purchased
            else:
                return 0

        return 1


class QuestTag(models.Model):
    name = models.CharField('Название', max_length=255)
    description = models.CharField('Описание', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']


class DailyQuest(models.Model):
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Ежедневный квест'
        verbose_name_plural = 'Ежедневные квесты'

    def __str__(self):
        return self.title[:50]


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

    class Meta:
        verbose_name = 'Результат ежедневного квеста'
        verbose_name_plural = 'Результаты ежедневных квестов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client} - {self.quest}'


class WeeklyQuest(models.Model):
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Еженедельный квест'
        verbose_name_plural = 'Еженедельные квесты'

    def __str__(self):
        return self.title


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


class ClientActionBuying(models.Model):
    client = models.ForeignKey(Client, models.CASCADE, 'purchased_actions')
    action = models.CharField('Действие', max_length=100, choices=Actions)
    count = models.IntegerField('Количество')
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Покупка пользователя'
        verbose_name_plural = 'Покупки пользователей'
        ordering = ['-date']

    def __str__(self):
        return f'{self.client} - {Actions(self.action).label}'


class MonthText(models.Model):
    text = models.TextField('Текст')
    audio_file_id = models.TextField(
        'ID аудиофайла в телеграм',
        null=True,
        blank=True,
    )
    type = models.CharField('Тип', max_length=100, choices=MonthTextTypes)
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'forecasts',
        verbose_name='Пользователь',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    objects = MonthTextManager()

    class Meta:
        verbose_name = 'Текст из "Месяц с Soul Muse"'
        verbose_name_plural = 'Тексты из "Месяц с Soul Muse"'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'[{MonthTextTypes(self.type).label}] '
            f'{self.client} - {self.text[:25]}'
        )


class DailyQuestTag(models.Model):
    quest = models.ForeignKey(DailyQuest, models.CASCADE, 'tags')
    tag = models.ForeignKey(QuestTag, models.CASCADE, 'daily_quests')


class WeeklyQuestTag(models.Model):
    quest = models.ForeignKey(WeeklyQuest, models.CASCADE, 'tags')
    tag = models.ForeignKey(QuestTag, models.CASCADE, 'weekly_quests')


class SoulMuseQuestion(models.Model):
    category = models.CharField('Категория', max_length=50)
    reason = models.TextField('Причина')
    question = models.TextField('Вопрос')
    answer = models.TextField('Ответ', blank=True)
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос к Soul Muse'
        verbose_name_plural = 'Вопросы к Soul Muse'
        ordering = ['-date']

    def __str__(self):
        return f'[{self.category}] {self.question[:50]}'


class MiniConsult(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'mini_consults',
        verbose_name='Пользователь',
    )
    text = models.TextField('Текст', blank=True)
    audio_file_id = models.TextField(
        'ID аудиофайла в телеграм',
        null=True,
        blank=True,
    )
    expert_type = models.CharField(
        'Тип эксперта',
        max_length=50,
        choices=ExpertTypes,
    )
    intention = models.CharField(
        'Намерение',
        max_length=50,
        choices=Intentions,
    )
    experience_type = models.CharField(
        'Уже сталкивался',
        max_length=50,
        choices=ExperienceTypes,
    )
    feelings_type = models.CharField(
        'Как себя чувствует',
        max_length=50,
        choices=FeelingsTypes,
    )
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Мини-консультация'
        verbose_name_plural = 'Мини-консультации'
        ordering = ['-date']

    def __str__(self):
        return f'{self.client} - {self.date}'


class Topic(models.Model):
    name = models.CharField('Метка', max_length=50, unique=True)
    is_global = models.BooleanField('Виден всем', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'
        ordering = ['name']


class MiniConsultTopic(models.Model):
    consult = models.ForeignKey(MiniConsult, models.CASCADE, 'topics')
    topic = models.ForeignKey(Topic, models.CASCADE, 'consults')


class MiniConsultFeedback(models.Model):
    consult = models.ForeignKey(MiniConsult, models.CASCADE, 'feedbacks')
    rating = models.CharField(
        'Оценка',
        max_length=50,
        choices=MiniConsultFeedbackRatings,
    )
    text = models.TextField('Текст', blank=True)
    audio_file_id = models.TextField(
        'ID аудиофайла в телеграм',
        null=True,
        blank=True,
    )
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Фидбек после мини-консультации'
        verbose_name_plural = 'Фидбек после мини-консультаций'
        ordering = ['-date']

    def __str__(self):
        return f'{self.consult} - {MiniConsultFeedbackRatings(self.rating)}'


class ExpertAnswer(models.Model):
    expert = models.ForeignKey(
        Client,
        models.CASCADE,
        'answers',
        verbose_name='Эксперт',
    )
    consult = models.ForeignKey(MiniConsult, models.CASCADE, 'answers')
    audio_file_id = models.TextField('ID аудиофайла в телеграм')
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Ответ эксперта'
        verbose_name_plural = 'Ответы экспертов'
        ordering = ['-date']

    def __str__(self):
        return f'{self.expert} - {self.consult}'


class FridayGift(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'friday_gifts',
        verbose_name='Пользователь',
    )
    type = models.CharField(
        'Тип подарка',
        max_length=50,
        choices=FridayGiftTypes,
    )
    text = models.TextField('Текст', blank=True)
    audio_file_id = models.TextField(
        'ID аудиофайла в телеграм',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    objects = FridayGiftManager()

    class Meta:
        verbose_name = 'Пятничный подарок'
        verbose_name_plural = 'Пятничные подарки'
        ordering = ['-created_at']

    def __str__(self):
        title = (
            f'[{self.created_at.strftime(settings.DATE_FMT)}] {self.client}'
        )
        if self.text:
            title += f' - {self.text[:50]}'
        return title


class Insight(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'insights',
        verbose_name='Пользователь',
    )
    text = models.TextField('Текст', blank=True)
    audio_file_id = models.TextField(
        'ID аудиофайла в телеграм',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Инсайт'
        verbose_name_plural = 'Инсайты'
        ordering = ['-created_at']

    def __str__(self):
        title = (
            f'[{self.created_at.strftime(settings.DATE_FMT)}] {self.client}'
        )
        if self.text:
            title += f' - {self.text[:50]}'
        return title
