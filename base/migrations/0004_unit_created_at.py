# Generated by Django 5.0.3 on 2024-03-09 09:53

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_pricing_reservation_userrole_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]