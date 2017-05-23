# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-23 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0009_auto_20170523_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='autocheckout_secret_code_checksum',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='Checksum used for autocheckout'),
        ),
        migrations.AlterField(
            model_name='member',
            name='telephone_number',
            field=models.CharField(blank=True, default='', max_length=32, verbose_name='Last name of the member'),
        ),
    ]