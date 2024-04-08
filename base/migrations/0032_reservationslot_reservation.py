# Generated by Django 5.0.3 on 2024-04-08 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_alter_category_category_capacity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationslot',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slots', to='base.reservation'),
        ),
    ]
