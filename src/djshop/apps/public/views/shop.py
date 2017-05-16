# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from djangovirtualpos.models import VirtualPointOfSale

from djshop.apps.offers.models import BundleOffer, GroupOffer
from djshop.apps.public.forms import ShoppingCartCheckoutForm
from djshop.apps.public.shopping_cart import SelectedProduct
from djshop.apps.sale.models import Sale
from djshop.apps.store.models import Product


# View shopping cart
def view_shopping_cart(request):
    if request.method == "POST":
        form = ShoppingCartCheckoutForm(request.POST)

        if form.is_valid():
            shopping_cart = request.session["shopping_cart"]
            selected_products = SelectedProduct.get_selected_products(request)
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            telephone_number = form.cleaned_data.get("telephone_number")
            email = form.cleaned_data.get("email")
            sale = Sale.factory_from_shopping_cart(shopping_cart, selected_products, first_name, last_name, telephone_number, email)
            del request.session["shopping_cart"]
            return HttpResponseRedirect(reverse("public:shopping_cart_checkout", args=(sale.code,)))
    else:
        form = ShoppingCartCheckoutForm()

    replacements = {"form": form}
    if "shopping_cart" in request.session and len(request.session["shopping_cart"]["products"].keys()) > 0:
        selected_products = SelectedProduct.get_selected_products(request)

        replacements["products"] = selected_products
        replacements["total_price"] = request.session["shopping_cart"]["total_price"]
        replacements["final_price"] = request.session["shopping_cart"]["final_price"]
        replacements["group_offer"] = None if request.session["shopping_cart"]["group_offer_id"] is None else GroupOffer.objects.get(id=request.session["shopping_cart"]["group_offer_id"])

    return render(request, "public/shop/view_shopping_cart.html", replacements)


# Add product to shopping cart
@csrf_exempt
def add_to_cart(request):
    if request.method != "POST":
        raise Http404

    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id, is_public=True)
    if product.price_type == "price_per_unit":
        amount = request.POST.get("units")
    else:
        amount = request.POST.get("grams")

    if amount == "" or amount <= 0:
        return HttpResponseRedirect(reverse("index"))

    if "shopping_cart" not in request.session:
        request.session["shopping_cart"] = {"total_price": 0, "final_price": 0, "group_offer_id": None, "products": {}}

    # If the product is already present in the shopping cart, increase its amount
    if request.session["shopping_cart"]["products"].get(product_id):
        selected_product = SelectedProduct.from_json(request.session["shopping_cart"]["products"].get(product_id))
        selected_product.add_product_amount(amount=amount)

    # Otherwise, the product is not in the shopping cart
    else:
        selected_product = SelectedProduct(product=product, amount=amount)

    # Check if there is some bundle offer that can be applied
    for bundle_offer in BundleOffer.objects.filter(product=selected_product.product):
        if bundle_offer.can_apply_discount(selected_product):
            selected_product.add_bundle_offer(bundle_offer)

    request.session["shopping_cart"]["products"][product_id] = selected_product.to_json()
    request.session["shopping_cart"]["total_price"] += float(selected_product.final_price)
    request.session["shopping_cart"]["final_price"] += float(selected_product.final_price)

    # Update group offer
    _update_shopping_chart(request)

    # Session has been modified
    request.session.modified = True

    # Redirect to shop
    return HttpResponseRedirect(reverse("index"))


# Remove product from shopping cart
@csrf_exempt
def remove_from_cart(request):

    if request.method != "POST":
        raise Http404

    if "shopping_cart" not in request.session:
        return HttpResponseRedirect(reverse("index"))

    selected_product_id = request.POST.get("selected_product_id")

    if selected_product_id not in request.session["shopping_cart"]["products"]:
        raise Http404

    selected_product = SelectedProduct.from_json(request.session["shopping_cart"]["products"][selected_product_id])

    request.session["shopping_cart"]["total_price"] -= selected_product.final_price
    request.session["shopping_cart"]["final_price"] = request.session["shopping_cart"]["total_price"]

    # Delete selected product
    del request.session["shopping_cart"]["products"][selected_product_id]

    # Update group offer
    _update_shopping_chart(request)

    # Session has been modified
    request.session.modified = True

    return HttpResponseRedirect(reverse("public:view_shopping_cart"))


def shopping_cart_checkout(request, sale_code):
    sale = Sale.objects.get(code=sale_code)
    virtual_point_of_sales = VirtualPointOfSale.objects.all()
    replacements = {
        "sale": sale,
        "virtual_point_of_sales": virtual_point_of_sales,
        "url_ok": request.build_absolute_uri(reverse("public:sale_ok", kwargs={"sale_code": sale.code})),
        "url_nok": request.build_absolute_uri(reverse("public:sale_cancel", kwargs={"sale_code": sale.code})),
    }
    return render(request, "public/shop/shopping_cart_checkout.html", replacements)


# Apply group offer if needed
def _update_shopping_chart(request):
    request.session["shopping_cart"]["final_price"] = float(request.session["shopping_cart"]["total_price"])
    request.session["shopping_cart"]["group_offer_id"] = None
    selected_products = SelectedProduct.get_selected_products(request)
    for group_offer in GroupOffer.objects.all():
        # Check if group offer can be applied to the set of selected products
        if group_offer.is_applicable(selected_products):
            # In that case, get discounted price and store that this shopping cart enjoys a discount (group offer)
            request.session["shopping_cart"]["group_offer_id"] = group_offer.id
            request.session["shopping_cart"]["final_price"] = group_offer.get_discounted_price(request.session["shopping_cart"]["final_price"])




