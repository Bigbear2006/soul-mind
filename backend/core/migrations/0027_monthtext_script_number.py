# Generated by Django 5.2.1 on 2025-05-22 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_remove_miniconsult_completed_client_expert_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthtext',
            name='script_number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Номер шаблона в сценарии месяца'),
        ),
    ]
