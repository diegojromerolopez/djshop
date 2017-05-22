from django.contrib import admin
from djshop.apps.sale.models import Sale, SaleDetail

admin.site.register(Sale)
admin.site.register(SaleDetail)