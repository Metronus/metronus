from django import forms
from django.utils.translation import ugettext_lazy as _


from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.task import Task

class TimeLogForm(forms.Form):
    description = forms.CharField(label=_("description"),max_length=200)
    workDate = forms.DateTimeField()
    duration = forms.IntegerField(label=_("duration"))
    timeLog_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, projectDepartment, *args, **kwargs):
        super(TimeLogForm, self).__init__(*args, **kwargs)
        tasks = Task.objects.filter(projectDepartment_id = projectDepartment.id)
        self.fields['task_id'] = forms.ModelChoiceField(queryset = tasks)

