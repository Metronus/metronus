from django import forms
from django.utils.translation import ugettext_lazy as _

class DepartmentForm(forms.Form):
    name = forms.CharField(label=_("name"),max_length=30)
    department_id=forms.IntegerField(widget=forms.HiddenInput())
