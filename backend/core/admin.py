from django.contrib import admin
from django.contrib.auth.models import Group
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.timezone import now
from rangefilter.filters import DateTimeRangeFilterBuilder

from bot.settings import settings
from core import models
from core.choices import PurchaseTypes, SubscriptionPlans
from core.filters import IsRegisteredFilter, SubscriptionPlanFilter
from core.mixins import AudioPlayerMixin
from core.models import SourceTag

admin.site.unregister(Group)

admin.site.register(models.QuestTag)
admin.site.register(models.Topic)


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
    extra = 1


class MiniConsultTopicInline(admin.TabularInline):
    model = models.MiniConsultTopic


@admin.register(models.DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    inlines = [DailyQuestTagInline]
    search_fields = ('title', 'text')


@admin.register(models.WeeklyQuest)
class WeeklyQuestAdmin(admin.ModelAdmin):
    inlines = [WeeklyQuestTagInline, WeeklyQuestTaskInline]


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    search_fields = ('first_name', 'fullname', 'username')
    list_filter = (
        'gender',
        SubscriptionPlanFilter,
        ('created_at', DateTimeRangeFilterBuilder()),
        'source_tag',
        IsRegisteredFilter,
    )
    list_select_related = ('source_tag',)
    list_display = ('first_name', 'username', 'fullname', 'email', 'birth')
    inlines = [ClientQuestTagInline, ClientExpertTypeInline]

    def save_model(
        self,
        request: HttpRequest,
        obj: models.Client,
        form: ModelForm,
        change: bool,
    ):
        old_obj = models.Client.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)

        subscription_changed = any(
            field in form.changed_data
            for field in ('subscription_end', 'subscription_plan')
        )
        if (
            not subscription_changed
            or not change
            or not form.cleaned_data.get('subscription_end')
        ):
            return

        old_sub_end = old_obj.subscription_end or now()
        added_sub_days = (
            form.cleaned_data['subscription_end'] - old_sub_end
        ).days
        if added_sub_days > 0:
            plan = form.cleaned_data['subscription_plan']
            if plan == SubscriptionPlans.STANDARD:
                purchase_type = PurchaseTypes.STANDARD_SUBSCRIPTION
            elif plan == SubscriptionPlans.PREMIUM:
                purchase_type = PurchaseTypes.PREMIUM_SUBSCRIPTION
            else:
                return

            models.Purchase.objects.create(
                client=obj,
                client_subscription=obj.get_current_plan(),
                purchase_type=purchase_type,
                value=added_sub_days,
                is_free=True,
            )


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


@admin.register(models.Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_select_related = ('client', 'client__source_tag')
    list_display = (
        'client',
        'purchase_type',
        'client_subscription',
        'is_free',
        'date',
    )
    list_filter = ('client_subscription', 'client__source_tag')


@admin.register(models.SourceTag)
class SourceTagAdmin(admin.ModelAdmin):
    readonly_fields = ('tag_link',)

    def tag_link(self, obj: SourceTag):
        return f'{settings.BOT_LINK}?start={obj.tag}'

    tag_link.short_description = 'Ссылка'
