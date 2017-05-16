from django import forms

from djshop.apps.club.models import Member


class MemberForm(forms.Form):
    class Meta:
        model = Member
        fields = ["first_name", "last_name", "credit_card_reference", "credit_card_reference_expiration_date"]