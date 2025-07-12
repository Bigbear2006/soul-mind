from datetime import timedelta

from django.contrib import admin
from django.db.models import Q
from django.utils.timezone import now


class IsRegisteredFilter(admin.SimpleListFilter):
    title = 'Зарегистрирован'
    parameter_name = 'is_registered'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Зарегистрирован'),
            ('no', 'Не зарегистрирован'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        filters = ~Q(aspects=[]) if self.value() == 'yes' else Q(aspects=[])
        return queryset.filter(filters)


class SubscriptionPlanFilter(admin.SimpleListFilter):
    title = 'Тип подписки'
    parameter_name = 'subscription'

    def lookups(self, request, model_admin):
        return [
            ('trial', 'Тестовый период'),
            ('standard', '✨ SoulMind Стандарт'),
            ('premium', '💎 SoulMind Премиум'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        if value == 'trial':
            return queryset.filter(created_at__gte=now() - timedelta(days=3))
        return queryset.filter(subscription_plan=value)
