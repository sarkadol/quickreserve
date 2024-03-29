# Generated by Django 4.2.6 on 2024-01-11 13:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_name', models.CharField(max_length=200)),
                ('to_date', models.DateTimeField()),
                ('from_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(max_length=200)),
                ('capacity', models.IntegerField()),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.offer')),
            ],
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
