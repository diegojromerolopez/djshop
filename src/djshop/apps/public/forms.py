# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


# Login form
from djshop.apps.club.models import Member, CreditCardReference


class LoginForm(forms.Form):
    username = forms.CharField(label=u"Username")
    password = forms.CharField(label=u"Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user = authenticate(username=cleaned_data.get("username"), password=cleaned_data.get("password"))

        if not user or not user.is_active:
            raise ValidationError(u"Your authentication data is invalid. Please check your username and password")

        cleaned_data["user"] = user
        return cleaned_data


# Checkout form for anonymous people
class AnonymousShoppingCartCheckoutForm(forms.Form):
    secret_code = forms.CharField(label="Secret code", required=False)
    first_name = forms.CharField(label=u"First name", required=False)
    last_name = forms.CharField(label=u"Last name", required=False)
    telephone_number = forms.CharField(label=u"Telephone number", required=False)
    email = forms.EmailField(label=u"Email", required=False)

    def clean(self):
        cleaned_data = super(AnonymousShoppingCartCheckoutForm, self).clean()
        if not cleaned_data.get("secret_code") and\
                (not cleaned_data.get("first_name") or not cleaned_data.get("last_name") or
                         not cleaned_data.get("telephone_number") or not cleaned_data.get("email")):
            raise ValidationError(u"Insert your secret code or your data")

        if cleaned_data.get("secret_code"):
            secret_code = cleaned_data.get("secret_code")
            try:
                secret_code_checksum = hashlib.sha256(secret_code).hexdigest()
                member = Member.objects.get(autocheckout_secret_code_checksum=secret_code_checksum)
                if member.current_credit_card_reference is None:
                    raise CreditCardReference.DoesNotExist
                cleaned_data["member"] = member
            except Member.DoesNotExist:
                raise ValidationError(u"Member does not exist")
            except CreditCardReference.DoesNotExist:
                raise ValidationError(u"Your membership has expired")

        return cleaned_data


# Checkout form for admins
class AdminShoppingCartCheckoutForm(forms.Form):
    member = forms.ChoiceField(label=u"Member", choices=[], required=False)
    first_name = forms.CharField(label=u"First name", required=False)
    last_name = forms.CharField(label=u"Last name", required=False)
    telephone_number = forms.CharField(label=u"Telephone number", required=False)
    email = forms.EmailField(label=u"Email", required=False)


    def __init__(self, *args, **kwargs):
        super(AdminShoppingCartCheckoutForm, self).__init__(*args, **kwargs)
        self.fields["member"].choices = [("", "Non-subscribed Customer")]+[
            (reference.member_id, reference.member.full_name)
            for reference in CreditCardReference.get_current_credit_card_references()
        ]

    def clean(self):
        cleaned_data = super(AdminShoppingCartCheckoutForm, self).clean()
        if not cleaned_data.get("member") and \
                (not cleaned_data.get("first_name") or not cleaned_data.get("last_name") or
                     not cleaned_data.get("telephone_number") or not cleaned_data.get("email")):
            raise ValidationError(u"Select a member or a non-subscribed customer")

        if cleaned_data.get("member"):
            cleaned_data["member"] = Member.objects.get(id=cleaned_data["member"])

        return cleaned_data
