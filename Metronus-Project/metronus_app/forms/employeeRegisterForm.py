from django import forms
from django.forms import Form


class EmployeeRegisterForm(Form):

    # User (Account data)
    username = forms.CharField()
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    # Employee (Actor) data
    identifier = forms.CharField(max_length=15)
    phone = forms.CharField(max_length=15)