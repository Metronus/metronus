from django.shortcuts import render
from metronus_app.forms.projectForm import ProjectForm
from metronus_app.model.project import Project,Company
from metronus_app.common_utils import get_current_admin_or_403
from django.http import HttpResponseRedirect
from metronus_app.model.administrator import Administrator
from populate_database import basicLoad
from django.core.exceptions             import ObjectDoesNotExist
from django.http                        import HttpResponseForbidden
from django.contrib.auth import authenticate,login



def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del proyecto

    template:
    project_form.html
    """
     # Check that the user is logged in
    admin = get_current_admin_or_403(request)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            createProject(form, admin)
            return HttpResponseRedirect('/project/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProjectForm(initial={"project_id":0})

    return render(request, 'project_form.html', {'form': form})


def list(request):
    """
    returns:
    projectos: lista de proyectos de la compañía logeada

    template:
    project_list.html
    """
     # Check that the user is logged in
    admin = get_current_admin_or_403(request)
    lista=Project.objects.filter(company_id=admin.company_id,deleted=False)
    return render(request, "project_list.html", {"projects": lista})


def edit(request,project_id):
    """
    parameters/returns:
    form: el formulario con los datos del proyecto

    template:
    project_form.html
    """
     # Check that the user is logged in
    admin = get_current_admin_or_403(request)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            project=Project.objects.get(pk=form.cleaned_data['project_id'])
            if checkCompanyProject(project,company_id=admin.company_id):
                updateProject(project,form)

            return HttpResponseRedirect('/project/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        project=Project.objects.get(pk=project_id)
        form = ProjectForm(initial={"name":project.name,"project_id":project.id})


    return render(request, 'project_form.html', {'form': form})

def delete(request,project_id):
    """
    parameters:
    project_id: the project id to delete

    returns:
    nothing

    template:
    project_list.html
    """
     # Check that the user is logged in
    admin = get_current_admin_or_403(request)
    project=Project.objects.get(pk=project_id)
    if checkCompanyProject(project,company_id=admin.company_id):
        deleteProject(project)
    return HttpResponseRedirect('/project/list')

#Auxiliar methods, containing the operation logic

def createProject(form, admin):
    pname=form.cleaned_data['name']
    company=admin.company_id
    Project.objects.create(name=pname,deleted=False,company_id=company)

def updateProject(project,form):
    project.name = form.cleaned_data['name']
    project.save()

def deleteProject(project):
    project.deleted=True
    project.save()

def checkCompanyProjectSession(project,admin):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProject(project,admin.company_id)

def checkCompanyProject(project,company_id):
    """
    checks if the project belongs to the specified company
    """
    return project is not None and company_id==project.company_id and project.deleted==False

def checkCompanyProjectIdSession(projectId,admin):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProjectId(projectId,admin.company_id)

def checkCompanyProjectId(projectId, companyId):
    """
    checks if the project belongs to the specified company
    """
    project = Project.objects.get(id = projectId, company_id=companyId, deleted=False)

    return project is not None

def get_current_admin(request):
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return None
