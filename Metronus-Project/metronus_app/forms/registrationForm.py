from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class RegistrationForm(Form):

    # Company
    cif = forms.CharField(label=_("cif"),max_length=9)
    company_name = forms.CharField(label=_("company_name"),max_length=100)
    short_name = forms.CharField(label=_("short_name"),max_length=50)
    company_email = forms.EmailField(label=_("company_email"))
    company_phone = forms.CharField(label=_("company_phone"),max_length=15)
    logo = forms.ImageField(label=_("logo"), required=False)
    
    # User (Account data)
    username = forms.CharField()
    admin_email = forms.EmailField(label=_("admin_email"))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)
    repeatPassword = forms.CharField(label=_("repeatPassword"), widget=forms.PasswordInput)
    first_name = forms.CharField(label=_("first_name"),max_length=50)
    last_name = forms.CharField(label=_("last_name"),max_length=50)

    # Administrator (Profile data)
    admin_identifier = forms.CharField(label=_("admin_identifier"),max_length=15)
    admin_phone = forms.CharField(label=_("admin_phone"),max_length=15)
    photo = forms.ImageField(label=_("photo"), required=False)
