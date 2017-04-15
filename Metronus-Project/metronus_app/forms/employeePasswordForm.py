from django import forms
from django.forms import Form


class EmployeePasswordForm(Form):
	"""Form for Employee password change"""
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)