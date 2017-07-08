from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from metronus_app.common_utils import phone_validator
from django.core.validators import MaxValueValidator, MinValueValidator


class EmployeeEditForm(Form):
    """Form for Employee profile editing"""
    # User (Account data)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    # Employee (Actor) data
    identifier = forms.CharField(max_length=15)
    phone = forms.CharField(max_length=9, validators=[phone_validator])
    photo = forms.ImageField(label=_("photo"), required=False)
    price_per_hour = forms.FloatField(label=_("price_per_hour"), initial="1.0", validators=[MinValueValidator(0.1, _("min_salary")), MaxValueValidator(1000000.0, _("max_salary"))])
