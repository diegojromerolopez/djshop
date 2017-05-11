# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from djangovirtualpos import views as djangovirtualpos_views

from djshop.apps.sale.models import Sale


@csrf_exempt
def set_payment_attributes(request):
    sale_model = Sale
    sale_ok_url = "public:sale_ok"
    sale_nok_url = "public:sale_cancel"
    return djangovirtualpos_views.set_payment_attributes(request, sale_model, sale_ok_url, sale_nok_url)


# Confirm sale
@csrf_exempt
def confirm_sale(request, virtualpos_type):
    """
    This view will be called by the bank.
    """
    return djangovirtualpos_views.confirm_payment(request, virtualpos_type, Sale)


# Sale completed successfully
def sale_ok(request, sale_code):
    sale = Sale.objects.get(code=sale_code, status="paid")
    replacements = {"sale": sale}
    return render(request, "public/sale/ok.html", replacements)


# Cancel sale
def sale_cancel(request, sale_code):
    sale = Sale.objects.get(code=sale_code, status="canceled")
    replacements = {"sale": sale}
    return render(request, "public/sale/cancel.html", replacements)
