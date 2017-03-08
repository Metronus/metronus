from django import forms
from django.forms import Form


class EmployeeEditForm(Form):

    # User (Account data)
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    # Employee (Actor) data
    identifier = forms.CharField(max_length=15)
    phone = forms.CharField(max_length=15)