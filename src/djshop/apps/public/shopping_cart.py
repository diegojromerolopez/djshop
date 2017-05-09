# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.utils import timezone

from djshop.apps.offers.models import BundleOffer
from djshop.apps.store.models import Product
import datetime


class SelectedProduct(object):

    def __init__(self, product, amount, total_price=None, bundle_offer=None, final_price=None, selection_datetime=None):
        super(SelectedProduct, self).__init__()

        self.product = product
        self.amount = amount

        if total_price is None:
            self.total_price = product.get_price(amount)
        else:
            self.total_price = total_price

        if selection_datetime is None:
            self.selection_datetime = timezone.now()
        else:
            self.selection_datetime = selection_datetime

        if bundle_offer is None:
            self.bundle_offer = None
            self.final_price = self.total_price
        else:
            self.bundle_offer = bundle_offer
            if final_price is None:
                raise ValueError(u"If there is a bundle offer present, there should be a final price")
            self.final_price = final_price

    @property
    def id(self):
        return self.product.id

    @property
    def categories(self):
        return self.product.categories.all()

    @property
    def name(self):
        return self.product.name

    @property
    def price(self):
        return self.product.price

    @property
    def price_type(self):
        return self.product.price_type

    @property
    def serving_size(self):
        return self.product.serving_size

    @property
    def main_image(self):
        return self.product.main_image

    # Add some amount to a product we already have in the shopping cart
    def add_product_amount(self, amount):
        self.amount = int(self.amount) + int(amount)
        self.total_price = self.product.get_price(self.amount)
        self.selection_datetime = timezone.now()

    # Add bundle offer to this selected product
    def add_bundle_offer(self, bundle_offer):
        discounted_price = bundle_offer.get_discounted_price(self)
        if discounted_price is not None:
            self.bundle_offer = bundle_offer
            self.final_price = discounted_price

    # Convert this selected product to JSON
    def to_json(self):
        obj_as_dict = {
            "product_id": self.product.id,
            "amount": float(self.amount),
            "total_price": float(self.total_price),
            "final_price": float(self.final_price),
            "bundle_offer_id": None if self.bundle_offer is None else self.bundle_offer.id,
            "selection_datetime": self.selection_datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        return json.dumps(obj_as_dict)

    # Get a selected product from a JSON string
    @staticmethod
    def from_json(json_selected_product):
        dict_selected_product = json.loads(json_selected_product)
        product = Product.objects.get(id=dict_selected_product["product_id"], is_public=True)
        amount = dict_selected_product["amount"]
        total_price = dict_selected_product["total_price"]
        final_price = dict_selected_product["final_price"]
        return SelectedProduct(
            product=product, amount=amount, total_price=total_price,
            bundle_offer=None if dict_selected_product["bundle_offer_id"] is None else BundleOffer.objects.get(id=dict_selected_product["bundle_offer_id"]),
            final_price=final_price,
            selection_datetime=datetime.datetime.strptime(
                dict_selected_product["selection_datetime"],
                "%Y-%m-%d %H:%M:%S"
            )
        )

    # Return the list of selected products of the shopping cart
    @staticmethod
    def get_selected_products(request):
        selected_products = []
        for json_selected_product in request.session["shopping_cart"]["products"].values():
            selected_product = SelectedProduct.from_json(json_selected_product)
            selected_products.append(selected_product)
        return selected_products
