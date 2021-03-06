# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from djangovirtualpos import views as djangovirtualpos_views

from djshop.apps.sale.models import Sale


@csrf_exempt
def set_payment_attributes(request):
    sale_model = Sale
    sale_ok_url = "public:sale_ok"
    sale_nok_url = "public:sale_cancel"
    reference_number = False
    if request.method == "POST" and request.POST.get("reference_number"):
        reference_number = request.POST.get("reference_number")
    return djangovirtualpos_views.set_payment_attributes(request, sale_model, sale_ok_url, sale_nok_url, reference_number)


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
    sale = Sale.objects.get(Q(status="canceled")|Q(status="pending"), code=sale_code)
    replacements = {"sale": sale}
    return render(request, "public/sale/cancel.html", replacements)
