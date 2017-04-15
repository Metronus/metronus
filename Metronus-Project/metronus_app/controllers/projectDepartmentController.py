from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from metronus_app.forms.projectDepartmentForm import ProjectDepartmentForm
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.controllers.projectController import checkCompanyProjectSession
from metronus_app.controllers.departmentController import checkCompanyDepartmentSession

from django.http                                 import HttpResponseRedirect
from metronus_app.common_utils                   import get_current_admin_or_403


def create(request):
    """
    parameters/returns:
    form: el formulario con los datos de la clase ProjectDepartment: project_id, department_id;
    y projectDepartment_id, que será 0 en caso de que estemos creando uno.

    template:
    projectdepartment_create.html
    """

    admin = get_current_admin_or_403(request)

    if request.method == 'POST':
        form = ProjectDepartmentForm(data=request.POST, user=admin)

        if form.is_valid():
            createProjectDepartment(form, admin)
            return render(request, 'projectdepartment_create.html', {'form': ProjectDepartmentForm(user=admin), 'success': True})

    #GET -> Create an empty form
    else:
        form = ProjectDepartmentForm(initial={"project_id":0, "department_id":0, "projectDepartment_id":0}, user=admin)

    return render(request, 'projectdepartment_form.html', {'form': form})


def delete(request):
    """
    parameters:
    Recibe el id del projectDepartment a borrar: projectDepartment_id

    template: projectDepartment_list.html
    """

    admin = get_current_admin_or_403(request)
    project_department_id = request.GET.get("projectDepartment_id")
    projectDepartment = get_object_or_404(ProjectDepartment, id=project_department_id)

    deleteProjectDepartment(projectDepartment, admin)

    return HttpResponseRedirect('/projectdepartment/list/')


def list(request):
    """
    parameters: project_id or department_id, both optional.
    If it receives project_id, it will return all projectDepartments from that project
    If it receives department_id, it will return all projectDepartments form that department
    If it receives none, it will return all projectDeparments from the logged company

    returns:
    projectDepartments: lista de relaciones proyecto-departamento de la compañía logeada, según el parámetro pasado. 

    template:
    projectdepartment_list.html
    """

    admin = get_current_admin_or_403(request)
    project_id = request.GET.get('project_id')
    department_id = request.GET.get('department_id')

    if project_id is not None:
        project = get_object_or_404(Project, id=project_id)
        checkCompanyProjectSession(project, admin)
        lista = ProjectDepartment.objects.filter(project_id=project)

    elif department_id is not None:
        department = get_object_or_404(Department, id=department_id)
        checkCompanyDepartmentSession(department, admin)
        lista = ProjectDepartment.objects.filter(department_id=department)

    else:
        lista = ProjectDepartment.objects.filter(project_id__company_id = admin.company_id)

    return render(request, "projectdepartment_list.html", {"projectDepartments": lista})


def edit(request):
    """
    Will not be used
    """
    admin = get_current_admin_or_403(request)
    if request.method == 'POST':
        form = ProjectDepartmentForm(data=request.POST, user=admin)

        if form.is_valid():
            projectDepartment=ProjectDepartment.objects.get(pk=form.cleaned_data['projectDepartment_id'])

            updateProjectDepartment(projectDepartment,form,admin)

            return HttpResponseRedirect('/projectdepartment/list')

    #GET -> Create an empty form
    else:
        projectDepartment=request.GET.get('projectDepartment_id')
        projectDepartment=get_object_or_404(ProjectDepartment, id=projectDepartment)
        form = ProjectDepartmentForm(
            initial={"department_id":projectDepartment.department_id,
                     "project_id":projectDepartment.project_id},
                     user=admin)

    return render(request, 'projectdepartment_form.html', {'form': form})


#Auxiliar methods, containing the operation logic

def createProjectDepartment(form, admin):
    project=form.cleaned_data['project_id']
    department = form.cleaned_data['department_id']

    legalForm = checkCompanyProjectSession(project, admin) and checkCompanyDepartmentSession(department, admin)
    if not legalForm:
        raise PermissionDenied

    return ProjectDepartment.objects.create(project_id = project, department_id = department)


#Se permitirán los updates de projectDepartment? -> Nope
def updateProjectDepartment(projectDepartment, form, admin):
    projectDepartment.project_id = form.cleaned_data['project_id']
    projectDepartment.department_id = form.cleaned_data['department_id']

    if not checkCompanyProjectDepartmentSession(projectDepartment, admin):
        raise PermissionDenied

    return projectDepartment.save()


def deleteProjectDepartment(projectDepartment, admin):
    if not checkCompanyProjectDepartmentSession(projectDepartment, admin):
        raise PermissionDenied

    projectDepartment.delete()


#Utility methods, mostly checkers

def checkCompanyProjectDepartmentSession(projectDepartment, admin):
    """
    checks if the projectDepartment belongs to the logged company, and neither project nor department are deleted
    """
    return checkCompanyProjectDepartment(projectDepartment,admin)


def checkCompanyProjectDepartment(projectDepartment, admin):
    """
    checks if the projectDepartment belongs to the specified company, and neither project nor department are deleted
    """
    res = checkCompanyProjectSession(projectDepartment.project_id, admin)
    res = res and checkCompanyDepartmentSession(projectDepartment.department_id, admin)

    return res
