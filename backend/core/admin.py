from django.contrib import admin
from django.contrib.auth.models import Group

from core import models
from core.models import SoulMuseQuestion

admin.site.unregister(Group)

admin.site.register(models.QuestTag)
admin.site.register(models.Topic)


class DailyQuestTagInline(admin.TabularInline):
    model = models.DailyQuestTag


class WeeklyQuestTagInline(admin.TabularInline):
    model = models.WeeklyQuestTag


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


@admin.register(models.ClientDailyQuest)
class ClientDailyQuestAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'quest')


@admin.register(models.WeeklyQuestTask)
class WeeklyQuestTaskAdmin(admin.ModelAdmin):
    list_select_related = ('quest',)


@admin.register(models.ClientWeeklyQuestTask)
class ClientWeeklyQuestTaskAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'quest', 'quest__quest')


@admin.register(models.MonthText)
class MonthForecastAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
    readonly_fields = ('created_at',)


@admin.register(SoulMuseQuestion)
class SoulMuseQuestion(admin.ModelAdmin):
    readonly_fields = ('date',)


@admin.register(models.MiniConsult)
class MiniConsultAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
    inlines = [MiniConsultTopicInline]


@admin.register(models.MiniConsultFeedback)
class MiniConsultFeedbackAdmin(admin.ModelAdmin):
    list_select_related = ('consult',)


@admin.register(models.ExpertAnswer)
class ExpertAnswerAdmin(admin.ModelAdmin):
    list_select_related = ('expert', 'consult')


@admin.register(models.FridayGift)
class FridayGiftAdmin(admin.ModelAdmin):
    list_select_related = ('client',)


@admin.register(models.Insight)
class InsightAdmin(admin.ModelAdmin):
    list_select_related = ('client',)
