# Generated by Django 5.0.3 on 2024-03-12 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_alter_unit_unit_name_alter_unit_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='max_count_of_units',
            field=models.IntegerField(default=1),
        ),
    ]
