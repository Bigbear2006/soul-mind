# Generated by Django 5.2 on 2025-04-25 01:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_client_centers_alter_client_gates_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='houses',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(), blank=True, default=list, null=True, size=None, verbose_name='Дома'),
        ),
    ]
