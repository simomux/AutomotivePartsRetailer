# Generated by Django 5.0.6 on 2024-07-03 07:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_order_name_alter_order_surname'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
