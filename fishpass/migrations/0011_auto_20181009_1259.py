# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-09 19:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishpass', '0010_auto_20181005_1644'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='barrier',
            options={'verbose_name': 'Barrier', 'verbose_name_plural': 'Barriers'},
        ),
        migrations.AlterModelOptions(
            name='barriercost',
            options={'verbose_name': 'Barrier Cost', 'verbose_name_plural': 'Barrier Costs'},
        ),
        migrations.AlterModelOptions(
            name='barrierstatus',
            options={'verbose_name': 'Barrier Status', 'verbose_name_plural': 'Barrier Statuses'},
        ),
        migrations.AlterModelOptions(
            name='barriertype',
            options={'verbose_name': 'Barrier Type', 'verbose_name_plural': 'Barrier Types'},
        ),
        migrations.AlterModelOptions(
            name='focusarea',
            options={'verbose_name': 'Focus Area', 'verbose_name_plural': 'Focus Areas'},
        ),
        migrations.AlterModelOptions(
            name='ownershiptype',
            options={'verbose_name': 'Ownership Type', 'verbose_name_plural': 'Ownership Types'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': 'Project', 'verbose_name_plural': 'Projects'},
        ),
        migrations.AlterModelOptions(
            name='projectreport',
            options={'verbose_name': 'Project Report', 'verbose_name_plural': 'Project Reports'},
        ),
        migrations.AlterModelOptions(
            name='projectreportbarrier',
            options={'verbose_name': 'Project Report Barrier', 'verbose_name_plural': 'Project Report Barriers'},
        ),
        migrations.AlterModelOptions(
            name='scenariobarrier',
            options={'verbose_name': 'Project-Specific Barrier Setting', 'verbose_name_plural': 'Project-Specific Barrier Settings'},
        ),
        migrations.AlterModelOptions(
            name='scenariobarrierstatus',
            options={'verbose_name': 'Project-Specific Barrier Status Setting', 'verbose_name_plural': 'Project-Specific Barrier Status Settings'},
        ),
        migrations.AlterModelOptions(
            name='scenariobarriertype',
            options={'verbose_name': 'Project-Specific Barrier Type Setting', 'verbose_name_plural': 'Project-Specific Barrier Type Settings'},
        ),
        migrations.AddField(
            model_name='project',
            name='spatial_organization',
            field=models.CharField(blank=True, choices=[('HUC08', 'HUC08'), ('HUC10', 'HUC10'), ('HUC12', 'HUC12'), ('County', 'County'), ('Region', 'Region'), ('State', 'State')], default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='geometry_final_area',
            field=models.FloatField(blank=True, null=True, verbose_name='Total Area'),
        ),
        migrations.AlterField(
            model_name='project',
            name='planning_units',
            field=models.TextField(blank=True, null=True, verbose_name='Planning Unit IDs'),
        ),
    ]
