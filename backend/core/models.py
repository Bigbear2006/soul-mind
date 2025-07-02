import random
from datetime import datetime, timedelta
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.timezone import now

from bot.loader import bot, logger
from bot.settings import settings
from bot.text_templates.base import all_centers_ordered
from bot.text_templates.friday_gift import friday_gifts_preambles
from bot.utils.formatters import date_to_str, genderize
from core.choices import (
    Actions,
    ExperienceTypes,
    ExpertTypes,
    FeelingsTypes,
    FridayGiftTypes,
    Genders,
    Intentions,
    MiniConsultFeedbackRatings,
    MiniConsultStatuses,
    MonthTextTypes,
    QuestStatuses,
    SubscriptionPlans,
)
from core.managers import (
    ClientManager,
    FridayGiftManager,
    MonthTextManager,
    PaymentManager,
)


class User(AbstractUser):
    pass


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
        models.SET_NULL,
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
    subscription_end = models.DateTimeField(
        verbose_name='Дата окончания подписки',
        null=True,
        blank=True,
    )
    email = models.EmailField('Почта', null=True, blank=True)
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
    birth_place = models.CharField(
        'Место рождения',
        max_length=255,
        blank=True,
    )
    birth_latitude = models.FloatField('Широта', null=True, blank=True)
    birth_longitude = models.FloatField('Долгота', null=True, blank=True)
    tzone = models.FloatField('Часовой пояс', null=True, blank=True)
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
    aspects = models.JSONField(
        verbose_name='Аспекты',
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
        if self.fullname:
            username += f' | {self.fullname}'
        if self.birth:
            username += f' - {date_to_str(self.birth)}'
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
        return bool(self.aspects)

    async def get_month_usages(self, action: Actions):
        today = now()
        return await ClientAction.objects.filter(
            client=self,
            action=action,
            date__month=today.month,
            date__year=today.year,
        ).acount()

    async def get_remaining_usages(self, action: Actions) -> int:
        client_action = await self.get_action(action)
        return client_action.free_limit + client_action.extra_limit

    async def get_action(self, action: Actions) -> 'ClientActionLimit':
        return await ClientActionLimit.objects.aget(client=self, action=action)

    def get_month_free_limit(self, action: Actions):
        if action == Actions.COMPATABILITY_ENERGY:
            if self.subscription_is_active():
                if self.subscription_plan == SubscriptionPlans.PREMIUM:
                    return 999  # unlimited
                else:
                    return 3
            elif self.has_trial():
                return 1
            else:
                return 0

        elif action == Actions.SOUL_MUSE_QUESTION:
            if self.subscription_is_active():
                if self.subscription_plan == SubscriptionPlans.PREMIUM:
                    return 15
                else:
                    return 4
            elif self.has_trial():
                return 1
            else:
                return 0

        elif action == Actions.WEEKLY_QUEST:
            if self.subscription_is_active():
                if self.subscription_plan == SubscriptionPlans.PREMIUM:
                    return 2
                else:
                    return 1

        return 0

    async def update_limit(self, action: Actions):
        return await ClientActionLimit.objects.filter(
            client=self,
            action=action,
        ).aupdate(
            free_limit=self.get_month_free_limit(action),
            subscription_plan=self.subscription_plan,
            updated_at=now(),
        )

    async def add_extra_usages(self, action: Actions, count: int):
        return await ClientActionLimit.objects.filter(
            client=self,
            action=action,
        ).aupdate(
            extra_limit=models.F('extra_limit') + count,
            updated_at=now(),
        )

    async def refresh_limit(self, action: Actions):
        today = now()

        try:
            client_action = await self.get_action(action)
        except ObjectDoesNotExist:
            await ClientActionLimit.objects.acreate(
                client=self,
                action=action,
                subscription_plan=self.subscription_plan,
                free_limit=self.get_month_free_limit(action),
                updated_at=today,
            )
            return

        if (
            # if limit wasn't updated 30 days and more
            client_action.updated_at < today - timedelta(days=30)
            # if trial is ended
            or (
                (client_action.updated_at - self.created_at).days
                < 3
                < (today - self.created_at).days
            )
            # if subscription plan was changed
            or client_action.subscription_plan != self.subscription_plan
            # if subscription is ended
            or (
                self.subscription_end
                and now() > self.subscription_end > client_action.updated_at
            )
        ):
            await self.update_limit(action)

    async def refresh_limits(self):
        await self.refresh_limit(Actions.SOUL_MUSE_QUESTION)
        await self.refresh_limit(Actions.COMPATABILITY_ENERGY)

    async def spend_usage(self, action: Actions):
        client_action = await self.get_action(action)

        if client_action.free_limit > 0:
            await ClientActionLimit.objects.filter(
                client=self,
                action=action,
            ).aupdate(free_limit=models.F('free_limit') - 1)
            return

        await ClientActionLimit.objects.filter(
            client=self,
            action=action,
        ).aupdate(extra_limit=models.F('extra_limit') - 1)

    def genderize(self, text: str) -> str:
        return genderize(text, gender=self.gender, prefix='gender')

    def get_priority_center(self) -> str:
        if not self.centers:
            return ''

        return sorted(
            self.centers,
            key=lambda x: all_centers_ordered.index(x),
        )[0]

    async def get_today_quest(self) -> Optional['ClientDailyQuest']:
        today = now().date()
        try:
            quest = (
                await ClientDailyQuest.objects.filter(client=self)
                .select_related('quest')
                .alatest('created_at')
            )
            if quest.created_at.date() == today:
                return quest
        except ObjectDoesNotExist:
            pass

        all_quests_ids = await sync_to_async(
            lambda: set(
                DailyQuest.objects.filter(
                    tags__tag_id__in=self.tags.values_list(
                        'tag_id',
                        flat=True,
                    ),
                ).values_list('id', flat=True),
            ),
        )()

        sent_quests_ids = await sync_to_async(
            lambda: set(
                ClientDailyQuest.objects.filter(
                    client=self,
                    status=QuestStatuses.COMPLETED,
                ).values_list('quest_id', flat=True),
            ),
        )()

        quest = await DailyQuest.objects.aget(
            pk=random.choice(list(all_quests_ids - sent_quests_ids)),
        )
        await ClientDailyQuest.objects.acreate(
            client=self,
            quest=quest,
        )
        return await self.get_today_quest()

    def get_month_weekly_quests(self):
        today = now()
        return ClientWeeklyQuest.objects.filter(
            client=self,
            date__month=today.month,
            date__year=today.year,
        )

    async def get_month_weekly_quests_count(self):
        return await self.get_month_weekly_quests().acount()

    async def get_month_weekly_quest_number(self, pk: int | str):
        ids = await sync_to_async(
            lambda: list(
                self.get_month_weekly_quests()
                .order_by('date')
                .values_list('quest_id', flat=True),
            ),
        )()
        if pk not in ids:
            return 0
        return ids.index(pk) + 1

    async def can_earn_points_on_weekly_quests(self):
        limit = self.get_month_free_limit(Actions.WEEKLY_QUEST)
        quests_count = await self.get_month_weekly_quests_count()
        return limit - quests_count > 0

    async def get_previous_month_script(self) -> Optional['MonthText']:
        try:
            return await MonthText.objects.filter(
                client=self,
                type=MonthTextTypes.MONTH_SCRIPT,
            ).alatest('created_at')
        except ObjectDoesNotExist:
            return


class ExpertType(models.Model):
    name = models.CharField(max_length=255, unique=True, choices=ExpertTypes)

    class Meta:
        verbose_name = 'Тип эксперта'
        verbose_name_plural = 'Типы экспертов'

    def __str__(self):
        return ExpertTypes(self.name).label


class ClientExpertType(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'expert_types',
        verbose_name='Пользователь',
    )
    expert_type = models.ForeignKey(
        ExpertType,
        models.CASCADE,
        'clients',
        verbose_name='Тип эксперта',
    )

    class Meta:
        verbose_name = 'Тип эксперта'
        verbose_name_plural = 'Типы экспертов'


##############
### QUESTS ###
##############


class DailyQuest(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Текст')
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
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Описание')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Еженедельный квест'
        verbose_name_plural = 'Еженедельные квесты'

    def __str__(self):
        return self.title


class WeeklyQuestTask(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Текст')
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
    is_active = models.BooleanField('Активен', default=True)

    def __str__(self):
        return f'[{self.day} день] {self.quest}'

    class Meta:
        unique_together = ('quest', 'day')
        verbose_name = 'Задача еженедельного квеста'
        verbose_name_plural = 'Задачи еженедельных квестов'

    def to_message_text(self):
        return (
            f'Челлендж «{self.quest.title}»\n\n'
            f'День {self.day}: «{self.title}»\n'
            f'{self.text}'
        )


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


class QuestTag(models.Model):
    name = models.CharField('Название', max_length=255)
    description = models.CharField('Описание', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']


class DailyQuestTag(models.Model):
    quest = models.ForeignKey(DailyQuest, models.CASCADE, 'tags')
    tag = models.ForeignKey(QuestTag, models.CASCADE, 'daily_quests')

    class Meta:
        verbose_name = 'Тег ежедневного квеста'
        verbose_name_plural = 'Теги ежедневных квестов'

    def __str__(self):
        return f'Тег ежедневного квеста ({self.pk})'


class WeeklyQuestTag(models.Model):
    quest = models.ForeignKey(WeeklyQuest, models.CASCADE, 'tags')
    tag = models.ForeignKey(QuestTag, models.CASCADE, 'weekly_quests')

    class Meta:
        verbose_name = 'Тег еженедельного квеста'
        verbose_name_plural = 'Теги еженедельных квестов'

    def __str__(self):
        return f'Тег еженедельного квеста ({self.pk})'


class ClientQuestTag(models.Model):
    client = models.ForeignKey(Client, models.CASCADE, 'tags')
    tag = models.ForeignKey(QuestTag, models.CASCADE, 'clients')

    class Meta:
        verbose_name = 'Тег пользователя'
        verbose_name_plural = 'Теги пользователей'

    def __str__(self):
        return f'Тег пользователя ({self.pk})'


######################
### CLIENT ACTIONS ###
######################


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


class ClientActionLimit(models.Model):
    client = models.ForeignKey(Client, models.CASCADE, 'limits')
    action = models.CharField('Действие', max_length=100, choices=Actions)
    subscription_plan = models.CharField(
        'Тип подписки',
        choices=SubscriptionPlans,
        max_length=50,
        blank=True,
    )
    free_limit = models.PositiveIntegerField('Осталось')
    extra_limit = models.PositiveIntegerField('Докуплено', default=0)
    updated_at = models.DateTimeField('Последнее обновление лимитов')

    class Meta:
        unique_together = ('client', 'action')
        verbose_name = 'Лимит пользователя'
        verbose_name_plural = 'Лимиты пользователей'
        ordering = ['-updated_at']

    def __str__(self):
        return (
            f'{self.client} - {Actions(self.action).label} '
            f'({self.free_limit + self.extra_limit})'
        )


####################
### MINI CONSULT ###
####################


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
    audio_file_path = models.CharField(
        'Путь к файлу',
        max_length=255,
        blank=True,
    )
    photo_file_id = models.TextField(
        'ID аудиофайла в телеграм',
        null=True,
        blank=True,
    )
    expert_type = models.ForeignKey(
        ExpertType,
        models.SET_NULL,
        'mini_consults',
        null=True,
        verbose_name='Тип эксперта',
    )
    intention = models.CharField('Намерение', max_length=255)
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
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=MiniConsultStatuses,
        default=MiniConsultStatuses.WAITING,
    )

    class Meta:
        verbose_name = 'Мини-консультация'
        verbose_name_plural = 'Мини-консультации'
        ordering = ['-date']

    def __str__(self):
        return (
            f'[{self.date.strftime(settings.DATE_FMT)}] '
            f'{self.client} - {ExpertTypes(self.expert_type.name).label} '
            f'({MiniConsultStatuses(self.status).label})'
        )

    def to_message_text(self) -> str:
        intention = (
            Intentions(self.intention).label
            if self.intention in Intentions
            else self.intention
        )

        if self.client.subscription_is_active():
            priority = SubscriptionPlans(self.client.subscription_plan).label
        else:
            priority = 'Разовая покупка'

        topics = genderize(
            ', '.join([t.topic.name for t in self.topics.all()]),
            gender=self.client.gender,
        )

        text = (
            f'Приоритет: {priority}\n'
            f'Тип эксперта: {self.expert_type}\n'
            f'Намерение: {intention}\n'
            f'Уже сталкивался: {ExperienceTypes(self.experience_type).label}\n'
            f'Ощущения: {FeelingsTypes(self.feelings_type).label}\n'
            f'Метки: {topics}\n\n'
        )
        if self.expert_type.name in (
            ExpertTypes.ASTROLOGIST,
            ExpertTypes.HD_ANALYST,
        ):
            text += (
                f'Дата рождения: {self.client.birth.strftime(settings.DATE_FMT)}\n'
                f'Место рождения: {self.client.birth_place}'
            )
        if self.expert_type.name == ExpertTypes.NUMEROLOGIST:
            text += (
                f'Дата рождения: {self.client.birth.strftime("%d.%m.%Y")}\n'
                f'ФИО: {self.client.fullname}'
            )
        if self.expert_type in (ExpertTypes.ASTROLOGIST, ExpertTypes.HD_ANALYST, ExpertTypes.PSYCHOLOGIST):
            text += f'ФИО: {self.client.fullname}'
        return text

    def to_button_text(self):
        if self.audio_file_id:
            return f'Аудио от {self.date.strftime(settings.DATE_FMT)}'
        return self.text[:25]

    async def send_to(
        self,
        chat_id: int | str,
        reply_markup: InlineKeyboardMarkup,
    ):
        text = self.to_message_text()
        if self.audio_file_id:
            await bot.send_audio(
                chat_id,
                self.audio_file_id,
                caption=text,
                reply_markup=reply_markup,
            )
        else:
            text += f'\n\nВопрос:\n{self.text}'
            await bot.send_message(
                chat_id,
                text,
                reply_markup=reply_markup,
            )


class Topic(models.Model):
    name = models.CharField('Метка', max_length=50, unique=True)
    is_global = models.BooleanField('Видна всем', default=False)

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
    audio_file_path = models.CharField(
        'Путь к файлу',
        max_length=255,
        blank=True,
    )
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Фидбек после мини-консультации'
        verbose_name_plural = 'Фидбек после мини-консультаций'
        ordering = ['-date']

    def __str__(self):
        return (
            f'{self.consult} - {MiniConsultFeedbackRatings(self.rating).label}'
        )


class ExpertAnswer(models.Model):
    expert = models.ForeignKey(
        Client,
        models.CASCADE,
        'answers',
        verbose_name='Эксперт',
    )
    consult = models.ForeignKey(MiniConsult, models.CASCADE, 'answers')
    audio_file_id = models.TextField('ID аудиофайла в телеграм')
    audio_file_path = models.CharField('Путь к файлу', max_length=255)
    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Ответ эксперта'
        verbose_name_plural = 'Ответы экспертов'
        ordering = ['date']

    def __str__(self):
        return f'{self.expert} - {self.consult}'


#######################
### TEXTS AND AUDIO ###
#######################


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
    script_number = models.IntegerField(
        'Номер шаблона в сценарии месяца',
        null=True,
        blank=True,
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
        if self.type == FridayGiftTypes.CARDS:
            title += f' - {self.text.split(".")[0]}'
        elif self.text:
            title += f' - {self.text[:50]}'
        return title

    def to_button_text(self):
        if self.type == FridayGiftTypes.CARDS:
            return self.text.split('.')[0]
        elif self.text:
            return self.text[:25]
        return f'Аудио от {self.created_at.strftime(settings.DATE_FMT)}'

    async def send(
        self,
        msg: Message,
        client: Client,
        reply_markup: InlineKeyboardMarkup,
    ):
        preamble = client.genderize(friday_gifts_preambles[self.type])
        if self.type == FridayGiftTypes.SYMBOLS:
            await msg.answer(self.text, reply_markup=reply_markup)
        elif self.type == FridayGiftTypes.CARDS:
            await msg.answer_photo(
                self.audio_file_id,
                preamble,
                reply_markup=reply_markup,
            )
        elif self.type == FridayGiftTypes.INSIGHT_PHRASES:
            await msg.answer_audio(
                self.audio_file_id,
                preamble,
                reply_markup=reply_markup,
            )


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

    def to_button_text(self):
        if self.text:
            return self.text[:25]
        return f'Аудио от {self.created_at.strftime(settings.DATE_FMT)}'


class Payment(models.Model):
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'payments',
        verbose_name='Пользователь',
    )
    charge_id = models.CharField('ID платежа')
    payment_type = models.CharField('Тип оплаты')
    date = models.DateTimeField(auto_now_add=True)
    objects = PaymentManager()

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'
        ordering = ['-date']

    def __str__(self):
        return (
            f'[{date_to_str(self.date)}] {self.client} - {self.payment_type}'
        )
