# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-06 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20161206_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_serving_size',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Maximum serving size'),
        ),
        migrations.AddField(
            model_name='product',
            name='min_serving_size',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Minimum serving size'),
        ),
    ]
