# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-04 23:35
from __future__ import unicode_literals

from django.db import migrations


def default_serving_sizes(apps, schema_editor):
    ServingSize = apps.get_model("store", "ServingSize")
    for weight in [25, 100, 500, 1000, 1500, 2000]:
        serving_size = ServingSize(weight=weight)
        serving_size.save()


def default_product_categories(apps, schema_editor):
    ProductCategory = apps.get_model("store", "ProductCategory")
    category_names = ["Pizza", "Main courses", "Drinks", "Desserts", "Salads"]
    for category_name in category_names:
        category = ProductCategory(name=category_name)
        category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(default_serving_sizes),
        migrations.RunPython(default_product_categories),
    ]
