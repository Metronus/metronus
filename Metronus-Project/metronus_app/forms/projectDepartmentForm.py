from django import forms
from metronus_app.model.projectDepartment import Project, Department


class ProjectDepartmentForm(forms.Form):
    """
    Form for relating a project and a department
    """
    projectDepartment_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, user, *args, **kwargs):
        super(ProjectDepartmentForm, self).__init__(*args, **kwargs)
        self.fields['project_id'] = forms.ModelChoiceField(queryset=Project.objects.filter(
            company_id=user.company_id, deleted=False))
        self.fields['department_id'] = forms.ModelChoiceField(queryset=Department.objects.filter(
            company_id=user.company_id, active=True))
