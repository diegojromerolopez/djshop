from django import forms

from djshop.apps.club.models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["first_name", "last_name"]