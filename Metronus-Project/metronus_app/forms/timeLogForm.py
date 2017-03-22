from django import forms
from django.utils.translation import ugettext_lazy as _


from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.task import Task

class TimeLogForm(forms.Form):
    description = forms.CharField(label=_("description"),max_length=200,
                                  widget=forms.TextInput(attrs={'class':'form-control'}))
    workDate = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class':'form-control timepicker'}))
    duration = forms.IntegerField(label=_("duration"),
                                  widget=forms.NumberInput(attrs={'class':'form-control'}))

    timeLog_id = forms.IntegerField(widget=forms.HiddenInput())
    task_id = forms.IntegerField(widget=forms.HiddenInput())