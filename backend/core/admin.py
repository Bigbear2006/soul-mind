from django.contrib import admin
from django.contrib.auth.models import Group

from core import models

admin.site.register(models.Client)
admin.site.unregister(Group)
