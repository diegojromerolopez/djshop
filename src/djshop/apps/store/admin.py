from django.contrib import admin

from djshop.apps.store.models import Product, ServingSize
from djshop.apps.store.models import ProductCategory

admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ServingSize)