# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-05 22:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0004_auto_20170705_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentation',
            name='proposal',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='presentation', to='proposals.Proposal'),
        ),
    ]
