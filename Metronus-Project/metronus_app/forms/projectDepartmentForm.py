from django import forms
from django.utils.translation import ugettext_lazy as _

class ProjectDepartmentForm(forms.Form):
    projectDepartment_id = forms.IntegerField(widget=forms.HiddenInput())
    project_id = forms.IntegerField(label=_("project"), widget=forms.Select())
    department_id = forms.IntegerField(label=_("department"), widget=forms.Select())