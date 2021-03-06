# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-14 03:18
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishpass', '0015_auto_20181012_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenariobarriertype',
            name='barrier_specific',
        ),
        migrations.RemoveField(
            model_name='scenariobarriertype',
            name='fixable',
        ),
        migrations.AlterField(
            model_name='scenariobarriertype',
            name='default_cost',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='Default Cost of Mitigation'),
        ),
        migrations.AlterField(
            model_name='scenariobarriertype',
            name='default_post_passability',
            field=models.FloatField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], verbose_name='Post-passability'),
        ),
    ]
