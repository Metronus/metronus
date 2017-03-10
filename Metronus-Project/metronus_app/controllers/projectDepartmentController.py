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

    admin = get_current_admin_or_403(request)

    project = request.GET.get('project_id')
    department = request.GET.get('department_id')

    if (project is not None):
        checkCompanyProjectSession(project, admin)
        lista = ProjectDepartment.objects.filter(project_id=project)

    elif (department is not None):
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

            if checkCompanyProjectDepartmentSession(projectDepartment, admin):
                updateProjectDepartment(projectDepartment,form)

            return HttpResponseRedirect('/project/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        projectDepartment=request.GET.get('projectDepartment_id')
        projectDepartment=ProjectDepartment.objects.get(pk=projectDepartment)
        form = ProjectDepartmentForm(
            initial={"department_id":projectDepartment.department_id, "project_id":projectDepartment.project_id}, user=admin)

    return render(request, 'projectdepartment_form.html', {'form': form})


#Auxiliar methods, containing the operation logic

def createProjectDepartment(form):
    project=form.cleaned_data['project_id']
    department = form.cleaned_data['department_id']

    ProjectDepartment.objects.create(project_id = project, department_id = department)

#Se permitirán los updates de projectDepartment?
def updateProjectDepartment(projectDepartment,form):
    projectDepartment.project_id = form.cleaned_data['project_id']
    projectDepartment.department_id = form.cleaned_data['department_id']

    checkCompanyProjectDepartmentSession(projectDepartment)

    return projectDepartment.save()

def deleteProjectDepartment(projectDepartment):
    projectDepartment.delete()


def checkCompanyProjectDepartmentSession(projectDepartment, admin):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProjectDepartment(projectDepartment,admin.company_id)

def checkCompanyProjectDepartment(projectDepartment,company_id):
    """
    checks if the projectDepartment belongs to the specified company, and neither project nor department are deleted
    """
    res = checkCompanyProjectSession(projectDepartment.project_id)
    res = res and checkCompanyDepartmentSession(projectDepartment.department_id)

    return res
