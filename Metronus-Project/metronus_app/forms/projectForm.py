from django import forms
from django.utils.translation import ugettext_lazy as _

class ProjectForm(forms.Form):
    """Form for Project model class"""
    name = forms.CharField(label=_("name"),max_length=30)
    project_id=forms.IntegerField(widget=forms.HiddenInput())