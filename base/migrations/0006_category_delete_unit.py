# Generated by Django 5.0.3 on 2024-03-12 08:23

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_unit_additional_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50)),
                ('category_description', models.CharField(blank=True, max_length=1000, null=True)),
                ('category_capacity', models.IntegerField(default=1)),
                ('max_simultneous_reservations', models.IntegerField(default=1)),
                ('additional_time', models.DurationField(blank=True, null=True)),
                ('max_count_of_categories', models.IntegerField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('belongs_to_offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.offer')),
                ('category_pricing', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.pricing')),
            ],
        ),
        migrations.DeleteModel(
            name='Unit',
        ),
    ]
