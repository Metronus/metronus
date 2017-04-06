from django import forms
from django.forms import Form


class EmployeeEditForm(Form):

    # User (Account data)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    # Employee (Actor) data
    identifier = forms.CharField(max_length=15)
    phone = forms.CharField(max_length=15)