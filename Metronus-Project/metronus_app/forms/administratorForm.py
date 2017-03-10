from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class AdministratorForm(Form):

    user_email = forms.EmailField(label=_("user_email"))
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)
    first_name = forms.CharField(label=_("first_name"),max_length=50)
    last_name = forms.CharField(label=_("last_name"),max_length=50)

    # Administrator (Profile data)
    identifier = forms.CharField(label=_("admin_identifier"),max_length=15)
    phone = forms.CharField(label=_("user_phone"),max_length=15)
