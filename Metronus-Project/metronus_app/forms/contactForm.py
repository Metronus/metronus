from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _


class ContactForm(Form):
    """Form for contacting the team behind Metronus"""
    name = forms.CharField(label=_("name"))
    email = forms.EmailField(label=_("email"))
    subject = forms.CharField(label=_("subject"))
    body = forms.CharField(label=_("body"))

    copy_to_user = forms.BooleanField(label=_("copy_to_user"), required=False)
