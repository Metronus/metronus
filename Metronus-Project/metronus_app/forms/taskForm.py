from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions                      import PermissionDenied

from metronus_app.model.actor import Actor
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole


class TaskForm(forms.Form):
    name = forms.CharField(label=_("name"),max_length=30)
    description = forms.CharField(label=_("description"),max_length=200)
    task_id=forms.IntegerField(widget=forms.HiddenInput())
    project_id = forms.ModelChoiceField(queryset=Project.objects.all())
    department_id = forms.ModelChoiceField(queryset=Department.objects.all())
