# Generated by Django 5.0.3 on 2024-03-12 14:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_remove_reservation_belongs_to_offer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='belongs_to_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='base.category'),
            preserve_default=False,
        ),
    ]