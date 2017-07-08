from django import forms
from django.forms import Form


class EmployeePasswordForm(Form):
    """Form for Employee password change"""
    currentpass = forms.CharField(label="currentpass", widget=forms.PasswordInput)
    newpass1 = forms.CharField(label="newpass1", widget=forms.PasswordInput)
    newpass2 = forms.CharField(label="newpass2", widget=forms.PasswordInput)
    send_password_notification = forms.BooleanField(label="send_password_notification", required=False)
    notify_new_pass = forms.BooleanField(label="notify_new_pass", required=False)
