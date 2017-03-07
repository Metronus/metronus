from django import forms
from django.forms import Form


class CompanyForm(Form):

    # Company
    cif = forms.CharField(max_length=9)
    company_name = forms.CharField(max_length=100)
    short_name = forms.CharField(max_length=50)
    company_email = forms.EmailField()
    company_phone = forms.CharField(max_length=15)
    logo = forms.FileInput()

    # User (Account data)
    username = forms.CharField()
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    # Administrator (Profile data)
    identifier = forms.CharField(max_length=15)
    phone = forms.CharField(max_length=15)