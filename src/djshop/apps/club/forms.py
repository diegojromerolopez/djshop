from django import forms
from django.core.exceptions import ValidationError

from djshop.apps.club.models import Member
import hashlib

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields["autocheckout_secret_code1"] = forms.CharField(label="Introduce your secret code", widget=forms.PasswordInput, required=True)
        self.fields["autocheckout_secret_code2"] = forms.CharField(label="Introduce your secret code again", widget=forms.PasswordInput, required=True)
        if self.instance.autocheckout_secret_code_checksum:
            self.fields["autocheckout_secret_code1"].required = False
            self.fields["autocheckout_secret_code2"].required = False

    def clean(self):
        cleaned_data = super(MemberForm, self).clean()
        if cleaned_data.get("autocheckout_secret_code1") and\
                        cleaned_data.get("autocheckout_secret_code1") != cleaned_data.get("autocheckout_secret_code2"):
            raise ValidationError(u"Secret codes must be the same")

        if cleaned_data.get("autocheckout_secret_code1") and\
                        cleaned_data.get("autocheckout_secret_code1") == cleaned_data.get("autocheckout_secret_code2"):
            cleaned_data["autocheckout_secret_code_checksum"] = hashlib.sha256(cleaned_data["autocheckout_secret_code1"]).hexdigest()

        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get("autocheckout_secret_code_checksum"):
            self.instance.autocheckout_secret_code_checksum = self.cleaned_data.get("autocheckout_secret_code_checksum")

        super(MemberForm, self).save(commit=commit)