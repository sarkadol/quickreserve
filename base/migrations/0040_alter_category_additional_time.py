# Generated by Django 5.0.3 on 2024-04-18 12:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0039_managerprofile_manager_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='additional_time',
            field=models.DurationField(blank=True, default=datetime.timedelta(0), null=True),
        ),
    ]
