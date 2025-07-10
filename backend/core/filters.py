from django.contrib import admin
from django.db.models import Q


class IsRegisteredFilter(admin.SimpleListFilter):
    title = 'Зарегистрирован'
    parameter_name = 'is_registered'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Зарегистрирован'),
            ('no', 'Не зарегистрирован'),
        )

    def queryset(self, request, queryset):
        filters = ~Q(aspects=[]) if self.value() == 'yes' else Q(aspects=[])
        return queryset.filter(filters)
