from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from metronus_app.common_utils import phone_validator
from django.core.validators import MaxValueValidator, MinValueValidator


class EmployeeRegisterForm(Form):
    """Form for Employee registering"""
    # User (Account data)
    username = forms.CharField(label=_("username"),max_length=100, initial="")
    password1 = forms.CharField(label=_("password"), widget=forms.PasswordInput, initial="")
    password2 = forms.CharField(label=_("repeatPassword"), widget=forms.PasswordInput, initial="")
    first_name = forms.CharField(label=_("name"), max_length=30, initial="")
    last_name = forms.CharField(label=_("surname"), max_length=30, initial="")
    email = forms.EmailField(label=_("email"), initial="")

    # Employee (Actor) data
    phone = forms.CharField(label=_("phone"), max_length=9, initial="", validators=[phone_validator])
    identifier = forms.CharField(label=_("identifier"), max_length=15, initial="")
    photo = forms.ImageField(label=_("photo"), required=False)
    price_per_hour = forms.FloatField(label=_("price_per_hour"), initial="1.0", validators=[MinValueValidator(0.1, _("min_salary")), MaxValueValidator(1000000.0, _("max_salary"))])
