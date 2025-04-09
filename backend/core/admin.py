from django.contrib import admin
from django.contrib.auth.models import Group

from core import models

admin.site.unregister(Group)

admin.site.register(models.Client)
admin.site.register(models.DailyQuest)
admin.site.register(models.WeeklyQuest)


@admin.register(models.ClientDailyQuest)
class ClientDailyQuestAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'quest')


@admin.register(models.WeeklyQuestTask)
class WeeklyQuestTaskAdmin(admin.ModelAdmin):
    list_select_related = ('quest',)


@admin.register(models.ClientWeeklyQuestTask)
class ClientWeeklyQuestTaskAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'quest', 'quest__quest')
