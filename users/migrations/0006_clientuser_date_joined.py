# Generated by Django 5.2 on 2025-04-23 09:20

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_clientuser_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientuser',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
