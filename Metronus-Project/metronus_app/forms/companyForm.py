from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from metronus_app.common_utils import phone_validator


class CompanyForm(Form):
    """Form for page customisation for the company"""
    visible_short_name = forms.BooleanField(label=_("visible_short_name"), required=False)
    company_email = forms.EmailField(label=_("company_email"))
    company_phone = forms.CharField(label=_("company_phone"), max_length=15, validators=[phone_validator])
    logo = forms.ImageField(label=_("logo"), required=False)
