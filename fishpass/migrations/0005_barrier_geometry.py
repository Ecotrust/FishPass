# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-26 21:00
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fishpass', '0004_auto_20180925_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='barrier',
            name='geometry',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=None, null=True, srid=3857),
        ),
    ]
