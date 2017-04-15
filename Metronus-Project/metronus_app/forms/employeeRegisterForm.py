from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class EmployeeRegisterForm(Form):
    """Form for Employee registering"""
    # User (Account data)
    username = forms.CharField(label=_("username"))
    password1 = forms.CharField(label=_("password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("repeatPassword"), widget=forms.PasswordInput)
    first_name = forms.CharField(label=_("name"), max_length=50)
    last_name = forms.CharField(label=_("surname"), max_length=50)
    email = forms.EmailField(label=_("email"))

    # Employee (Actor) data
    phone = forms.CharField(label=_("phone"), max_length=15)
    identifier = forms.CharField(label=_("identifier"), max_length=15)
    photo = forms.ImageField(label=_("photo"), required = False)
    price_per_hour=forms.FloatField(label=_("price_per_hour"),initial="1.0")