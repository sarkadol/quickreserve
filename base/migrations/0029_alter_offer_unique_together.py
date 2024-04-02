# Generated by Django 5.0.3 on 2024-04-02 12:27

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_alter_category_closing_time_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='offer',
            unique_together={('offer_name', 'manager_of_this_offer')},
        ),
    ]
