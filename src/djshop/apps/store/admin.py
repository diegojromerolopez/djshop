from django.contrib import admin

# Register your models here.
from djshop.apps.store.models import Product, ServingSize
from djshop.apps.store.models import ProductCategory

admin.register(ProductCategory)
admin.register(Product)
admin.register(ServingSize)