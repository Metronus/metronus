from django import forms
from django.forms import Form


class EmployeePasswordForm(Form):
    """Form for Employee password change"""
    newpass1 = forms.CharField(label="newpass1", widget=forms.PasswordInput)
    newpass2 = forms.CharField(label="newpass2", widget=forms.PasswordInput)
    currentpass = forms.CharField(label="currentpass", widget=forms.PasswordInput)
