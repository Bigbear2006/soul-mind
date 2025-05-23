# Generated by Django 5.2 on 2025-04-09 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_client_subscription_end'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='birth',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время рождения'),
        ),
        migrations.AddField(
            model_name='client',
            name='birth_latitude',
            field=models.FloatField(null=True, verbose_name='Широта'),
        ),
        migrations.AddField(
            model_name='client',
            name='birth_longitude',
            field=models.FloatField(null=True, verbose_name='Долгота'),
        ),
        migrations.AddField(
            model_name='client',
            name='gender',
            field=models.CharField(blank=True, max_length=50, verbose_name='Пол'),
        ),
        migrations.AlterField(
            model_name='client',
            name='subscription_plan',
            field=models.CharField(blank=True, choices=[('standard', 'Стандартная'), ('premium', 'Премиум')], max_length=50, verbose_name='Тип подписки'),
        ),
    ]
