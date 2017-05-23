from __future__ import unicode_literals

import random

from django.core.exceptions import MultipleObjectsReturned
from django.db import models


# Each one of the members of the club
from django.db.models import Q
from django.utils import timezone
from djangovirtualpos.models import VPOSRedsys


class Member(models.Model):

    first_name = models.CharField(verbose_name=u"First name of the member", max_length=32)
    last_name = models.CharField(verbose_name=u"Last name of the member", max_length=32)
    telephone_number = models.CharField(verbose_name=u"Last name of the member", max_length=32, blank=True, default="")
    email = models.EmailField(verbose_name=u"Email of the member", blank=True, default="")

    autocheckout_secret_code_checksum = models.CharField(verbose_name=u"Checksum used for autocheckout", max_length=512, blank=True, default="")

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __unicode__(self):
        return self.full_name

    @property
    def current_credit_card_reference(self):
        try:
            now = timezone.now()
            this_year = now.year
            this_month = now.month
            return self.credit_card_references.\
                filter(
                    Q(expiration_year__gt=this_year) | (Q(expiration_year=this_year) & Q(expiration_month__lt=this_month)),
                    status="paid", reference_number__isnull=False
                ).exclude(
                    reference_number=""
                ).order_by("-id")[0]
        except IndexError:
            return None


# Credit card reference
class CreditCardReference(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("canceled", "Canceled"),
        ("paid", "Paid")
    )
    member = models.ForeignKey("club.Member", related_name=u"credit_card_references")
    code = models.CharField(verbose_name=u"Credit card sale operation code", max_length=64)
    reference_number = models.CharField(verbose_name=u"Credit card Reference number", max_length=64, blank=True, default="")
    operation_number = models.CharField(verbose_name=u"Credit Card Reference operation number", max_length=128, blank=True, default=None, null=True)
    status = models.CharField(verbose_name=u"Sale status", max_length=16, choices=STATUS_CHOICES, default="pending")
    expiration_month = models.PositiveIntegerField(verbose_name=u"Credit Card Reference expiration year", blank=True, default=None, null=True)
    expiration_year = models.PositiveIntegerField(verbose_name=u"Credit Card Reference expiration month", blank=True, default=None, null=True)
    virtual_pos = models.ForeignKey("djangovirtualpos.VirtualPointOfSale", verbose_name=u"Credit Card Reference virtual point of sale", blank=True, default=None, null=True)

    @property
    def description(self):
        description = "Reference {0} activation for member {1}".format(self.code, self.member.id)
        if self.status == "paid":
            description = "{0} (Reference #: {1}, Expiration date: {2})".format(
                description, self.reference_number, self.expiration_date
            )
        return description

    @property
    def expiration_date(self):
        return "{0}/{1}".format(self.expiration_month, self.expiration_year)

    def __unicode__(self):
        return self.description

    @property
    def amount(self):
        return 0

    def online_confirm(self):
        if hasattr(self, "virtual_pos"):
            virtual_pos = self.virtual_pos
            if hasattr(virtual_pos, "delegated") and type(virtual_pos.delegated) == VPOSRedsys:
                self.reference_number = virtual_pos.delegated.ds_merchantparameters.get("Ds_Merchant_Identifier")
                expiration_date = virtual_pos.delegated.ds_merchantparameters.get("Ds_ExpiryDate")
                self.expiration_month = int(expiration_date[2:])
                self.expiration_year = int("20{0}".format(expiration_date[:2]))
        self.status = "paid"
        self.save()

    @staticmethod
    def get_current_credit_card_references():
        now = timezone.now()
        this_year = now.year
        this_month = now.month
        return CreditCardReference.objects.\
            filter(
                Q(expiration_year__gt=this_year) |
                (
                    Q(expiration_year=this_year) &
                    Q(expiration_month__lt=this_month)
                ),
            status="paid", reference_number__isnull=False
        ).exclude(
            reference_number=""
        ).order_by("-id")

    @staticmethod
    def new(member):
        try:
            return CreditCardReference.objects.get(
                member=member, reference_number=None, operation_number=None, status="pending",
                expiration_month=None, expiration_year=None
            )
        except CreditCardReference.DoesNotExist:
            return CreditCardReference._new(member)
        except MultipleObjectsReturned:
            CreditCardReference.objects.filter(
                member=member, reference_number=None, operation_number=None, status="pending",
                expiration_month=None, expiration_year=None
            ).delete()
            return CreditCardReference._new(member)

    @staticmethod
    def _new(member):
        reference = CreditCardReference(member=member, code=CreditCardReference._new_code())
        reference.save()
        return reference

    @staticmethod
    def _new_code(code_size=9):
        return "".join(["{0}".format(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])) for i in range(0, code_size)])