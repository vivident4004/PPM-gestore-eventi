# Generated by Django 5.2.3 on 2025-06-21 10:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestoreEventi', '0004_alter_category_options_event_is_free_event_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='is_free_event',
        ),
        migrations.RemoveField(
            model_name='priceoption',
            name='currency',
        ),
        migrations.AddField(
            model_name='priceoption',
            name='max_seats',
            field=models.IntegerField(blank=True, null=True, verbose_name='max seats'),
        ),
        migrations.AddField(
            model_name='registration',
            name='price_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registrations', to='GestoreEventi.priceoption'),
        ),
    ]
