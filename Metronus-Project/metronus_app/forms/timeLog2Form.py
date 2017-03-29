from django import forms
from django.utils.translation import ugettext_lazy as _
from metronus_app.model.project import Project
from metronus_app.model.actor import Actor
from metronus_app.model.department import Department
from django.forms import ModelChoiceField
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.task import Task
from django.core.exceptions                      import PermissionDenied, ObjectDoesNotExist

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return  obj.name

class TimeLog2Form(forms.Form):
    description = forms.CharField(label=_("description"),max_length=200,
                                  widget=forms.TextInput(attrs={'class':'form-control'}))
    workDate = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class':'form-control timepicker'}))
    duration = forms.IntegerField(label=_("duration"),
                                  widget=forms.NumberInput(attrs={'class':'form-control'}))

    timeLog_id = forms.IntegerField(widget=forms.HiddenInput())
    task_id = MyModelChoiceField(queryset=None, widget=forms.Select(attrs={'class':'form-control'}))
    project_id = MyModelChoiceField(queryset=None, widget=forms.Select(attrs={'class':'form-control'}))
    department_id = MyModelChoiceField(queryset=None, widget=forms.Select(attrs={'class':'form-control'}))


    produced_units = forms.FloatField(label=_("produced_units"),required=False,initial="")
    def __init__(self, request,*args, **kwargs):
        super(TimeLog2Form, self).__init__(*args, **kwargs)
        actor=None
        if not request.user.is_authenticated():
            raise PermissionDenied
        try:
            actor= Actor.objects.get(user=request.user)
        except ObjectDoesNotExist:
            raise PermissionDenied
        projects = Project.objects.filter(company_id=actor.company_id,deleted=False)

        self.fields['project_id'].queryset = projects