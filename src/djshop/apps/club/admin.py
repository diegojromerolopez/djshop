from django.contrib import admin

from djshop.apps.club.models import CreditCardReference, Member

admin.site.register(Member)
admin.site.register(CreditCardReference)