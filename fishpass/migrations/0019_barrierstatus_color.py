# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-06 22:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishpass', '0018_auto_20181127_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='barrierstatus',
            name='color',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
