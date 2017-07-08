from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from metronus_app.common_utils import phone_validator

class AdministratorForm(Form):
    """Form for Administrator model class"""
    admin_email = forms.EmailField(label=_("admin_email"))
    first_name = forms.CharField(label=_("first_name"), max_length=30)
    last_name = forms.CharField(label=_("last_name"), max_length=30)
    identifier = forms.CharField(label=_("admin_identifier"), max_length=15)
    phone = forms.CharField(label=_("admin_phone"), max_length=9, validators=[phone_validator])
    photo = forms.ImageField(label=_("photo"), required=False)
