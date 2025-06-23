from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from rangefilter.filters import DateTimeRangeFilterBuilder

from bot.settings import settings
from core import models

admin.site.unregister(Group)

admin.site.register(models.QuestTag)
admin.site.register(models.Topic)


class AudioPlayerMixin:
    def audio_player(self, obj):
        url = (
            f'https://api.telegram.org/file/bot{settings.BOT_TOKEN}/'
            f'{obj.audio_file_path}'
        )
        return mark_safe(
            f'<audio controls src="{url}">'
            'Ваш браузер не поддерживает элемент audio.'
            '</audio>',
        )

    audio_player.short_description = 'Аудио'


class DailyQuestTagInline(admin.TabularInline):
    model = models.DailyQuestTag


class WeeklyQuestTagInline(admin.TabularInline):
    model = models.WeeklyQuestTag


class ClientQuestTagInline(admin.TabularInline):
    model = models.ClientQuestTag


class ClientExpertTypeInline(admin.TabularInline):
    model = models.ClientExpertType


class WeeklyQuestTaskInline(admin.StackedInline):
    model = models.WeeklyQuestTask


class MiniConsultTopicInline(admin.TabularInline):
    model = models.MiniConsultTopic


@admin.register(models.DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    inlines = [DailyQuestTagInline]


@admin.register(models.WeeklyQuest)
class WeeklyQuestAdmin(admin.ModelAdmin):
    inlines = [WeeklyQuestTagInline]


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    search_fields = ('fullname', 'username')
    list_filter = (
        'subscription_plan',
        ('created_at', DateTimeRangeFilterBuilder()),
    )
    inlines = [ClientQuestTagInline, ClientExpertTypeInline]


@admin.register(models.ClientDailyQuest)
class ClientDailyQuestAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'quest')
    readonly_fields = ('created_at',)


@admin.register(models.WeeklyQuestTask)
class WeeklyQuestTaskAdmin(admin.ModelAdmin):
    list_select_related = ('quest',)


@admin.register(models.ClientWeeklyQuestTask)
class ClientWeeklyQuestTaskAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'quest', 'quest__quest')
    readonly_fields = ('created_at',)


@admin.register(models.ClientActionLimit)
class ClientActionLimitAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
    readonly_fields = ('updated_at',)


@admin.register(models.MiniConsult)
class MiniConsultAdmin(admin.ModelAdmin, AudioPlayerMixin):
    list_select_related = ('client', 'expert_type')
    readonly_fields = ('audio_player',)
    inlines = [MiniConsultTopicInline]


@admin.register(models.MiniConsultFeedback)
class MiniConsultFeedbackAdmin(admin.ModelAdmin, AudioPlayerMixin):
    list_select_related = ('consult',)
    readonly_fields = ('audio_player',)


@admin.register(models.ExpertAnswer)
class ExpertAnswerAdmin(admin.ModelAdmin, AudioPlayerMixin):
    list_select_related = ('expert', 'consult')
    readonly_fields = ('audio_player',)


@admin.register(models.MonthText)
class MonthForecastAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
    readonly_fields = ('created_at',)


@admin.register(models.SoulMuseQuestion)
class SoulMuseQuestion(admin.ModelAdmin):
    readonly_fields = ('date',)


@admin.register(models.FridayGift)
class FridayGiftAdmin(admin.ModelAdmin):
    list_select_related = ('client',)


@admin.register(models.Insight)
class InsightAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
