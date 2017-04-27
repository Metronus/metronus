from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class AdministratorForm(Form):
    """Form for Administrator model class"""
    admin_email = forms.EmailField(label=_("admin_email"))
    #password = forms.CharField(label=_("password"), widget=forms.PasswordInput)
    #repeatPassword = forms.CharField(label=_("repeatPassword"), widget=forms.PasswordInput)
    first_name = forms.CharField(label=_("first_name"), max_length=50)
    last_name = forms.CharField(label=_("last_name"), max_length=50)

    # Administrator (Profile data)
    identifier = forms.CharField(label=_("admin_identifier"), max_length=15)
    phone = forms.CharField(label=_("admin_phone"), max_length=15)
    photo = forms.ImageField(label=_("photo"), required=False)
