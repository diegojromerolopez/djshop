from __future__ import unicode_literals

from django.db import models, transaction
from django.utils import timezone
from djshop.apps.offers.models import GroupOffer, BundleOffer
import random


class Sale(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("canceled", "Canceled"),
        ("paid", "Paid")
    )
    status = models.CharField(verbose_name=u"Sale status", max_length=16, choices=STATUS, default="pending")

    first_name = models.CharField(verbose_name=u"First name", max_length=128)
    last_name = models.CharField(verbose_name=u"Last name", max_length=128)

    telephone_number = models.CharField(verbose_name=u"Telephone number", max_length=32)
    email = models.EmailField(verbose_name=u"Email")

    code = models.CharField(verbose_name=u"Sale unique code", max_length=16)
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    operation_number = models.CharField(verbose_name=u"Sale operation number", max_length=128)

    online_payment_code = models.CharField(verbose_name=u"Online payment code", max_length=64, default=None, null=True)
    payment_datetime = models.DateTimeField(verbose_name=u"Online payment datetime", default=None, null=True)

    total_price = models.DecimalField(verbose_name=u"Total price for this sale",
                                      help_text="Price for this sale not including discount",
                                      decimal_places=2, max_digits=10)

    group_offer_name = models.CharField(max_length=128, verbose_name=u"Name of the offer", default="", blank=True)

    group_offer_discount_amount = models.DecimalField(
        verbose_name=u"Discount amount", decimal_places=2, max_digits=10, default=0
    )

    group_offer_discount_type = models.CharField(
        verbose_name=u"Discount type (percent or absolute)",
        max_length=32, choices=GroupOffer.DISCOUNT_TYPE, null=True, blank=True, default=None
    )

    final_price = models.DecimalField(verbose_name=u"Final price for this sale",
                                      help_text="Price for this sale including discount",
                                      decimal_places=2, max_digits=10)

    @staticmethod
    def get_random_code(size=16):
        return ''.join(random.choice("0123456789") for _ in range(size))

    @staticmethod
    def factory_from_shopping_cart(shopping_cart, selected_products, first_name, last_name, telephone_number, email):
        # Shopping cart data
        total_price = shopping_cart["total_price"]
        final_price = shopping_cart["final_price"]
        sale = Sale(
            first_name=first_name, last_name=last_name, telephone_number=telephone_number, email=email,
            code=Sale.get_random_code(), creation_datetime=timezone.now(),
            total_price=total_price, final_price=final_price
        )

        # If there is an offer
        if shopping_cart["group_offer_id"]:
            group_offer = GroupOffer.objects.get(id=shopping_cart["group_offer_id"])
            sale.group_offer_name = group_offer.name
            sale.group_offer_discount_amount = group_offer.discount_amount
            sale.group_offer_discount_type = group_offer.discount_type

        sale.save()

        # Selected products of the shopping cart
        for selected_product in selected_products:
            SaleDetail.create_from_selected_product(selected_product, sale)

        return sale

    # Description used in VPOS
    @property
    def description(self):
        return u"Sale {0} made by {1} {2}".format(self.code, self.first_name, self.last_name)

    # Online confirm
    def online_confirm(self):
        self.status = "paid"
        self.save()


# Sale detail
class SaleDetail(models.Model):
    sale = models.ForeignKey("sale.Sale", verbose_name=u"Sale", related_name="sale_details")

    product_name = models.CharField(max_length=128, verbose_name=u"Name of the product")
    product_price = models.DecimalField(verbose_name=u"Price of this product",
                                        help_text="Default price of this product", decimal_places=2, max_digits=10)
    product_price_type = models.CharField(verbose_name=u"Product price type", max_length=32, default="price_per_weight")

    amount = models.PositiveIntegerField(verbose_name=u"Amount of product",
                                    help_text="Amount of product selected by customer")

    total_price = models.DecimalField(verbose_name=u"Total price for this product selection",
                                      help_text="Price for the amount of product selected by user",
                                      decimal_places=2, max_digits=10)

    bundle_offer_name = models.CharField(max_length=128, verbose_name=u"Name of the product", default="", blank=True)
    bundle_offer_bundle_product_units = models.PositiveIntegerField(verbose_name=u"Number of units in the bundle",
                                                                    default=None, null=True)
    bundle_offer_paid_product_units = models.PositiveIntegerField(verbose_name=u"Number of units the customer must pay",
                                                                  default=None, null=True)

    final_price = models.DecimalField(verbose_name=u"Final price for this product selection",
                                      help_text="Price for the amount of product selected by user including discount",
                                      decimal_places=2, max_digits=10)

    @staticmethod
    def create_from_selected_product(selected_product, sale):
        product = selected_product.product
        sale_detail = SaleDetail(
            sale=sale, product_name=product.name, product_price=product.price, product_price_type=product.price_type,
            amount=selected_product.amount,
            total_price=selected_product.total_price, final_price=selected_product.final_price
        )

        if selected_product.bundle_offer:
            bundle_offer = selected_product.bundle_offer
            sale_detail.bundle_offer_name = bundle_offer.name
            sale_detail.bundle_offer_bundle_product_units = bundle_offer.bundle_product_units
            sale_detail.bundle_offer_paid_product_units = bundle_offer.paid_product_units

        sale_detail.save()

        return sale_detail
