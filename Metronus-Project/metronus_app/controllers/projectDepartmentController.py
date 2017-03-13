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
    form: el formulario con los datos de la clase ProjectDepartment: project_id y department_id

    template:
    proyectdepartment_form.html
    """

    admin = get_current_admin_or_403(request)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectDepartmentForm(data=request.POST, user=admin)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #print(form.cleaned_data["project_id"].deleted)
            pd = createProjectDepartment(form, admin)
            return render_to_response('projectdepartment_create.html', {'form': ProjectDepartmentForm(user=admin), 'success': True})

    # if a GET (or any other method) we'll create a blank form
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
    projectDepartment_id = request.GET.get("projectDepartment_id")
    projectDepartment = get_object_or_404(ProjectDepartment, id=projectDepartment_id)

    deleteProjectDepartment(projectDepartment, admin)

    return HttpResponseRedirect('/projectdepartment/list/')

def list(request):
    """
    parameters: project_id o department_id

    returns:
    projectDepartments: lista de relaciones proyecto-departamento de la compañía logeada, según el parámetro pasado. 

    template:
    proyectdepartment_list.html
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
    returns:
    form: el formulario con los datos de la clase ProjectDepartment: project_id y department_id

    template:
    projectdepartment_form.html
    """
    admin = get_current_admin_or_403(request)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectDepartmentForm(data=request.POST, user=admin)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            projectDepartment=ProjectDepartment.objects.get(pk=form.cleaned_data['projectDepartment_id'])

            updateProjectDepartment(projectDepartment,form,admin)

            return HttpResponseRedirect('/projectdepartment/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        projectDepartment=request.GET.get('projectDepartment_id')
        projectDepartment=get_object_or_404(ProjectDepartment, id=projectDepartment)
        form = ProjectDepartmentForm(
            initial={"department_id":projectDepartment.department_id, "project_id":projectDepartment.project_id}, user=admin)

    return render(request, 'projectdepartment_form.html', {'form': form})


#Auxiliar methods, containing the operation logic

def createProjectDepartment(form, admin):
    project=form.cleaned_data['project_id']
    department = form.cleaned_data['department_id']

    legalForm = checkCompanyProjectSession(project, admin) and checkCompanyDepartmentSession(department, admin)
    if not legalForm:
        raise PermissionDenied

    return ProjectDepartment.objects.create(project_id = project, department_id = department)

#Se permitirán los updates de projectDepartment?
def updateProjectDepartment(projectDepartment, form, admin):
    projectDepartment.project_id = form.cleaned_data['project_id']
    projectDepartment.department_id = form.cleaned_data['department_id']

    if not checkCompanyProjectDepartmentSession(projectDepartment, admin):
        raise PermissionDenied

    return projectDepartment.save()

def deleteProjectDepartment(projectDepartment, admin):
    # Check that the admin has permission to delete that projectDepartment
    if not checkCompanyProjectDepartmentSession(projectDepartment, admin):
        raise PermissionDenied

    projectDepartment.delete()


#---------------- UTILITY

def checkCompanyProjectDepartmentSession(projectDepartment, admin):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProjectDepartment(projectDepartment,admin)

def checkCompanyProjectDepartment(projectDepartment, admin):
    """
    checks if the projectDepartment belongs to the specified company, and neither project nor department are deleted
    """
    res = checkCompanyProjectSession(projectDepartment.project_id, admin)
    res = res and checkCompanyDepartmentSession(projectDepartment.department_id, admin)

    return res
