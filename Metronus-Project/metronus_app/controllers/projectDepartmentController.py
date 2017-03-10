from django.shortcuts import render
from metronus_app.forms.projectDepartmentForm import ProjectDepartmentForm
from metronus_app.model.projectDepartment import ProjectDepartment
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

            project = form.cleaned_data['project_id']
            department = form.cleaned_data['department_id']
            legalForm = checkCompanyProjectSession(project, admin) and checkCompanyDepartmentSession(department, admin)
            
            if (legalForm):
                createProjectDepartment(form)
                return HttpResponseRedirect('/project/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProjectDepartmentForm(initial={"project_id":0, "department_id":0, "projectDepartment_id":0}, user=admin)

    return render(request, 'projectdepartment_form.html', {'form': form})


def list(request):
    """
    parameters: project_id o department_id

    returns:
    projectDepartments: lista de relaciones proyecto-departamento de la compañía logeada, según el parámetro pasado. 

    template:
    proyectdepartment_list.html
    """

    projectId = request.GET.get('project_id')
    departmentId = request.GET.get('department_id')

    if (projectId is not None):
        checkCompanyProjectIdSession(projectId)
        lista = ProjectDepartment.objects.filter(project_id=projectId)

    elif (departmentId is not None):
        checkCompanyDepartmentIdSession(departmentId)
        lista = ProjectDepartment.objects.filter(department_id=departmentId)

    
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
        form = ProjectForm(data=request.POST, user=admin)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            projectDepartment=ProjectDepartment.objects.get(pk=form.cleaned_data['projectDepartment_id'])

            if checkCompanyProjectDepartmentSession(project, admin):
                updateProjectDepartment(projectDepartment,form)

            return HttpResponseRedirect('/project/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        projectDepartment_id=request.GET.get('projectDepartment_id')
        projectDepartment_id=ProjectDepartment.objects.get(pk=projectDepartment_id)
        form = ProjectDepartmentForm(
            initial={"department_id":projectDepartment.department_id, "project_id":projectDepartment.project_id}, user=admin)

    return render(request, 'projectdepartment_form.html', {'form': form})


#Auxiliar methods, containing the operation logic

def createProjectDepartment(form):
    if form.is_valid():
        project=form.cleaned_data['project_id']
        department = form.cleaned_data['department_id']

        ProjectDepartment.objects.create(project_id = project, department_id = department)

#Se permitirán los updates de projectDepartment?
def updateProjectDepartment(projectDepartment,form):
    if form.is_valid():
        projectDepartment.project_id = form.cleaned_data['project_id']
        projectDepartment.department_id = form.cleaned_data['department_id']

        checkCompanyProjectDepartmentSession(projectDepartment)

        projectDepartment.save()
        return projectDepartment

#TODO: Delete

def checkCompanyProjectDepartmentSession(projectDepartment):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProjectDepartment(projectDepartment,request.session['id'])

def checkCompanyProjectDepartment(projectDepartment,company_id):
    """
    checks if the projectDepartment belongs to the specified company, and neither project nor department are deleted
    """
    res = checkCompanyProjectIdSession(projectDepartment.project_id)
    res = res and checkCompanyDepartmentIdSession(projectDepartment.department_id)

    return res
