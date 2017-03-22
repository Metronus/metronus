from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions                      import PermissionDenied

from metronus_app.model.actor import Actor
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

from django.forms import ModelChoiceField
#custom model choice to display name
class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return  obj.name

class TaskForm(forms.Form):
    name = forms.CharField(label=_("name"),max_length=30)
    description = forms.CharField(label=_("description"),max_length=200)
    task_id=forms.IntegerField(widget=forms.HiddenInput())
    project_id = MyModelChoiceField(queryset=None)
    department_id = MyModelChoiceField(queryset=None)

    def __init__(self, request,*args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        actor=None
        if not request.user.is_authenticated():
            raise PermissionDenied
        try:
            actor= Actor.objects.get(user=request.user)
        except ObjectDoesNotExist:
            raise PermissionDenied

        if actor.user_type!='A':
            #not an admin
            isTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                        role_id__name= "Team manager")
            res=isTeamManager.count()>0

            if res:
                #is manager
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
            else:
                #not a manager
                rolesPro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                         role_id__name="Project manager")
                rolesDep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                         role_id__name="Coordinator")

                if  rolesPro.count()>0:
                    #you're a project manager. Loading your projects
                    proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                        projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
                    departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
                elif rolesDep.count()>0:
                    #you're a department coordinator. loading your departments
                    proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)
                    departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                        projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
                else:
                    #not any of this? get outta here!!
                    raise PermissionDenied

        else:
            #is admin
            proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)
            departamentos=Department.objects.filter(company_id=actor.company_id,active=True)


        self.fields['project_id'].queryset = proyectos
        self.fields['department_id'].queryset = departamentos
