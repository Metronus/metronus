from django import forms
from django.forms import Form


class RoleManagementForm(Form):
	"""Form for Role model class managing"""
    employee_id = forms.IntegerField(widget=forms.HiddenInput())
    department_id = forms.IntegerField()
    project_id = forms.IntegerField()
    employeeRole_id = forms.IntegerField()
    role_id = forms.IntegerField()
