# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from djangovirtualpos.models import VirtualPointOfSale, VPOSCantCharge

from djshop.apps.offers.models import BundleOffer, GroupOffer
from djshop.apps.public.forms import ShoppingCartCheckoutForm
from djshop.apps.public.shopping_cart import SelectedProduct
from djshop.apps.sale.models import Sale
from djshop.apps.store.models import Product
from django.http import JsonResponse


@csrf_exempt
def set_payment_attributes(request):

    if request.method == 'GET':
        return JsonResponse({"message":u"Método no válido para dicha operación."})

    else:
        # Obtenemos los objetos TPV y Sale
        try:
            # Obtenemos el objeto TPV
            virtual_point_of_sale = VirtualPointOfSale.get(id=request.POST["tpv_id"], is_erased=False)

            # Obtenemos el objeto Sale
            payment_code = request.POST["payment_code"]
            payment = Sale.objects.get(code=payment_code, status="pending")
            payment.virtual_point_of_sale = virtual_point_of_sale
            payment.save()

        except Sale.DoesNotExist as e:
            return JsonResponse({"message":u"La orden de pago no ha sido previamente creada."})

        except VirtualPointOfSale.DoesNotExist:
            return JsonResponse({"message": u"La pasarela de pagos no existe"})

        virtual_point_of_sale.configurePayment(
            # Cantidad a pagar
            amount=payment.amount,
            # Concepto del pago
            description=payment.inscription.first_name + "-" + payment.inscription.uuid,
            # Codigo del pago.
            sale_code=payment.code,
            # Urls de retorno.
            url_ok=request.build_absolute_uri(reverse("public:sale_ok", kwargs={"sale_code": payment.code})),
            url_nok=request.build_absolute_uri(reverse("public:sale_cancel", kwargs={"sale_code": payment.code})),
        )

        # Asigna un número de operación específico según el tipo de TPV
        # ¿Por qué hacemos esto? Porque puede que los TPVs tengan distintos
        # formatos de números de operación
        try:
            # Generamos un número de operacion y se lo asignamos.
            operation_number = virtual_point_of_sale.setupPayment()
            payment.update(operation_number=operation_number)
        except Exception as e:
            return JsonResponse({
                "message": u"Error al generar el número de operación {0}".format(e)
            })

        # Valores de los atributos del formulario de pago
        form_data = virtual_point_of_sale.getPaymentFormData()

        # Mensaje para hacer más sencilla la depuración
        form_data["message"] = "Pago {0} actualizado. Se devuelven los atributos del pago.".format(payment_code)

        # Devolvemos una respuesta HTTP con formato JSON
        return JsonResponse(form_data)


# Confirm sale
@csrf_exempt
def confirm_sale(request, virtualpos_type):
    """
    This view will be called by the bank.
    """

    # Checking if the Point of Sale exists
    virtual_pos = VirtualPointOfSale.receiveConfirmation(request, virtualpos_type=virtualpos_type)

    if not virtual_pos:
        # The VPOS does not exist, inform the bank with a cancel
        # response if needed
        return VirtualPointOfSale.staticResponseNok(virtualpos_type)

    # Verify if bank confirmation is indeed from the bank
    verified = virtual_pos.verifyConfirmation()
    operation_number = virtual_pos.operation.operation_number

    with transaction.atomic():
        try:
            # Getting your payment object from operation number
            payment = Sale.objects.get(operation_number=operation_number, status="pending")
        except Sale.DoesNotExist:
            return virtual_pos.responseNok("not_exists")

        if verified:
            # Charge the money and answer the bank confirmation
            try:
                response = virtual_pos.charge()
                # Implement the online_confirm method in your payment
                # this method will mark this payment as paid and will
                # store the payment date and time.
                payment.online_confirm()
            except VPOSCantCharge as e:
                return virtual_pos.responseNok(extended_status=e)
            except Exception as e:
                return virtual_pos.responseNok("cant_charge")

        else:
            # Payment could not be verified
            # signature is not right
            response = virtual_pos.responseNok("verification_error")

        return response


# Sale completed successfully
def sale_ok(request, sale_code):
    sale = Sale.objects.get(code=sale_code)
    replacements = {"sale": sale}
    return render(request, "public/sale/ok.html", replacements)


# Cancel sale
def sale_cancel(request, sale_code):
    sale = Sale.objects.get(code=sale_code)
    replacements = {"sale": sale}
    return render(request, "public/sale/cancel.html", replacements)
