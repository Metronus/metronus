from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions                      import PermissionDenied

from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
class TaskForm(forms.Form):
    name = forms.CharField(label=_("name"),max_length=30)
    description = forms.CharField(label=_("description"),max_length=200)
    task_id=forms.IntegerField(widget=forms.HiddenInput())
    
    def __init__(self, employee, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        isAdminOrTeamManager= ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                    role_id__name__in=["Administrator" , "Team manager"])
        roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                 role_id__name__in=["Project manager","Department manager","Coordinator"])

        if isAdminOrTeamManager.count()>0:
            proyectos=Project.objects.filter(company_id=employee.company_id)
            departamentos=Department.objects.filter(company_id=employee.company_id)
        elif roles.count()>0:
            proyectos=Project.objects.filter(company_id=employee.company_id)
            departamentos=Department.objects.filter(company_id=employee.company_id)
        else:
            raise PermissionDenied
        self.fields['project_id'] = forms.ModelChoiceField(queryset=proyectos)
        self.fields['department_id'] = forms.ModelChoiceField(queryset=departamentos)
