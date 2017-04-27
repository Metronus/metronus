from django import forms
from django.utils.translation import ugettext_lazy as _
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.forms import ModelChoiceField
from metronus_app.model.task import Task
from django.core.validators import MinValueValidator


class MyModelChoiceField(ModelChoiceField):
    """Custom Dropdown List which shows the name of the object instead of some weird or standard message"""
    def label_from_instance(self, obj):
        return obj.name


class TaskModelChoiceField(ModelChoiceField):
    """Custom Dropdown List which shows the name of the object instead of some weird or standard message"""

    def label_from_instance(self, obj):
        desc = obj.goal_description
        if desc is None or desc == "":
            desc = _('no_goal')
        return "{0} ({1})".format(obj.name, desc)


class TimeLog2Form(forms.Form):
    """Form for TimeLog model class"""
    project_id = MyModelChoiceField(label=_("project"), queryset=None,
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    department_id = MyModelChoiceField(label=_("department"), queryset=None,
                                       widget=forms.Select(attrs={'class': 'form-control'}))
    task_id = TaskModelChoiceField(label=_("task"), queryset=None, widget=forms.Select(attrs={'class': 'form-control'}))

    description = forms.CharField(label=_("description"), max_length=200, required=False, initial="",
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    workDate = forms.DateTimeField(label=_("workdate"), widget=forms.widgets.DateTimeInput(
                attrs={'class': 'form-control'}))
    duration = forms.IntegerField(label=_("duration"), validators=[MinValueValidator(0)],
                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))

    timeLog_id = forms.IntegerField(widget=forms.HiddenInput())

    produced_units = forms.FloatField(label=_("produced_units"),
                                      required=False, initial="", validators=[MinValueValidator(0)],
                                      widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, actor, *args, **kwargs):
        super(TimeLog2Form, self).__init__(*args, **kwargs)

        projects = Project.objects.filter(company_id=actor.company_id, deleted=False)

        self.fields['project_id'].queryset = projects
        self.fields['task_id'].queryset = Task.objects.filter(actor_id__company_id=actor.company_id, active=True)
        self.fields['department_id'].queryset = Department.objects.filter(company_id=actor.company_id, active=True)
