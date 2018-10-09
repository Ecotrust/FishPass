# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-09 21:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishpass', '0011_auto_20181009_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='barrier',
            name='accessible',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Accessible?'),
        ),
        migrations.AddField(
            model_name='barrier',
            name='likely_exp',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]