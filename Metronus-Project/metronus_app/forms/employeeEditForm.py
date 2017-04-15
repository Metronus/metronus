from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _

class EmployeeEditForm(Form):
    """Form for Employee profile editing"""
    # User (Account data)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    # Employee (Actor) data
    identifier = forms.CharField(max_length=15)
    phone = forms.CharField(max_length=15)

    price_per_hour=forms.FloatField(label=_("price_per_hour"),initial="1.0")