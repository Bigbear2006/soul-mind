# Generated by Django 5.2 on 2025-04-29 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_soulmusequestion_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='birth_place',
            field=models.CharField(blank=True, max_length=255, verbose_name='Место рождения'),
        ),
    ]
