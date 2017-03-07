from django.shortcuts import render
from metronus_app.forms.projectForm import ProjectForm
from metronus_app.model.project import Project,Company
from django.http import HttpResponseRedirect


def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del proyecto

    template:
    project_form.html
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            createProject(form, request)
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
    lista=Project.objects.filter(company_id=request.session['id'],deleted=False)
    return render(request, "project_list.html", {"projects": lista})


def edit(request):
    """
    parameters/returns:
    form: el formulario con los datos del proyecto

    template:
    project_form.html
    """
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
            if checkCompanyProject(project):
                updateProject(project,form)

            return HttpResponseRedirect('/project/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        project_id=request.GET.get('project_id')
        project=Project.objects.get(pk=project_id)
        form = ProjectForm(initial={"name":project.name,"project_id":project.id})


    return render(request, 'project_form.html', {'form': form})

def delete(request):
    """
    parameters:
    project_id: the project id to delete

    returns:
    nothing

    template:
    project_list.html
    """
    project_id=request.GET.get('project_id')
    project=Project.objects.get(pk=project_id)
    if checkCompanyProject(project):
        deleteProject(project)
    return HttpResponseRedirect('/project/list')

#Auxiliar methods, containing the operation logic

def createProject(form, request):
    pname=form.cleaned_data['name']
    company=Company.objects.get(pk=request.session['id'])
    Project.objects.create(name=pname,deleted=False,company_id=company)

def updateProject(project,form):
    project.name = form.cleaned_data['name']
    project.save()

def deleteProject(project):
    project.deleted=True
    project.save()

def checkCompanyProjectSession(project):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProject(project,request.session['id'])

def checkCompanyProject(project,company_id):
    """
    checks if the project belongs to the specified company
    """
    return project is not None and company_id==project.company_id and project.deleted==False

def checkCompanyProjectIdSession(projectId):
    """
    checks if the project belongs to the logged company
    """
    return checkCompanyProjectId(projectId,request.session['id'])

def checkCompanyProjectId(projectId, companyId):
    """
    checks if the project belongs to the specified company
    """
    project = Project.objects.get(id = projectId, company_id=companyId, deleted=False)
    
    return project is not None
