from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class CompanyForm(Form):

    # Company
    company_email = forms.EmailField(label=_("company_email"))
    company_phone = forms.CharField(label=_("company_phone"),max_length=15)
    logo = forms.ImageField(label=_("logo"))
