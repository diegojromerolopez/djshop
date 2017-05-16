from __future__ import unicode_literals

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
    STATUS = (
        ("pending", "Pending"),
        ("canceled", "Canceled"),
        ("paid", "Paid")
    )
    member = models.ForeignKey("club.Member", related_name=u"credit_card_references")
    code = models.CharField(verbose_name=u"Credit card sale operation code", max_length=64)
    reference_number = models.CharField(verbose_name=u"Credit card Reference number", max_length=64)
    operation_number = models.CharField(verbose_name=u"Credit Card Reference operation number", max_length=128)
    status = models.CharField(verbose_name=u"Sale status", max_length=16, choices=STATUS, default="pending")
    expiration_date = models.DateField(verbose_name=u"Credit Card Reference expiration date")
