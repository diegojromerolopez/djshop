# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from djangovirtualpos import views as djangovirtualpos_views

from djshop.apps.club.models import CreditCardReference
from djshop.apps.sale.models import Sale


@csrf_exempt
def set_attributes(request, member_id):
    sale_model = CreditCardReference
    sale_ok_url = "club:subscription_ok"
    sale_nok_url = "club:subscription_cancel"
    return djangovirtualpos_views.set_payment_attributes(request, sale_model, sale_ok_url, sale_nok_url, request_reference=True)


# Confirm sale
@csrf_exempt
def confirm(request, virtualpos_type):
    """
    This view will be called by the bank.
    """
    return djangovirtualpos_views.confirm_payment(request, virtualpos_type, CreditCardReference)


# Sale completed successfully
def ok(request, sale_code):
    reference = CreditCardReference.objects.get(code=sale_code)
    replacements = {"reference": reference, "member": reference.member}
    return render(request, "club/credit_card_references/subscription/ok.html", replacements)


# Cancel sale
def cancel(request, sale_code):
    reference = CreditCardReference.objects.get(code=sale_code)
    replacements = {"reference": reference, "member": reference.member}
    return render(request, "club/credit_card_references/subscription/cancel.html", replacements)
