# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-22 11:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_auto_20170522_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcardreference',
            name='reference_number',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Credit card Reference number'),
        ),
    ]