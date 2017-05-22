from django.contrib import admin
from djshop.apps.offers.models import GroupOffer, BundleOffer

admin.site.register(GroupOffer)
admin.site.register(BundleOffer)