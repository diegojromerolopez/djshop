from __future__ import unicode_literals

import random

from django.core.exceptions import MultipleObjectsReturned
from django.db import models


# Each one of the members of the club
class Member(models.Model):

    first_name = models.CharField(verbose_name=u"First name of the member", max_length=32)
    last_name = models.CharField(verbose_name=u"Last name of the member", max_length=32)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)


# Credit card reference
class CreditCardReference(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("canceled", "Canceled"),
        ("paid", "Paid")
    )
    member = models.ForeignKey("club.Member", related_name=u"credit_card_references")
    code = models.CharField(verbose_name=u"Credit card sale operation code", max_length=64)
    reference_number = models.CharField(verbose_name=u"Credit card Reference number", max_length=64, blank=True, default=None, null=True)
    operation_number = models.CharField(verbose_name=u"Credit Card Reference operation number", max_length=128, blank=True, default=None, null=True)
    status = models.CharField(verbose_name=u"Sale status", max_length=16, choices=STATUS_CHOICES, default="pending")
    expiration_date = models.DateField(verbose_name=u"Credit Card Reference expiration date", blank=True, default=None, null=True)

    @property
    def description(self):
        return "Reference {0} activation for member {1}".format(self.code, self.member.id)

    @property
    def amount(self):
        return 0

    @staticmethod
    def new_code(code_size=9):
        return "".join(["{0}".format(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])) for i in range(0, code_size)])

    @staticmethod
    def new(member):
        try:
            return CreditCardReference.objects.get(
                member=member, reference_number=None, operation_number=None, status="pending", expiration_date=None
            )
        except CreditCardReference.DoesNotExist:
            return CreditCardReference._new(member)
        except MultipleObjectsReturned:
            CreditCardReference.objects.filter(
                member=member, reference_number=None, operation_number=None, status="pending", expiration_date=None
            ).delete()
            return CreditCardReference._new(member)

    @staticmethod
    def _new(member):
        reference = CreditCardReference(member=member, code=CreditCardReference.new_code())
        reference.save()
        return reference