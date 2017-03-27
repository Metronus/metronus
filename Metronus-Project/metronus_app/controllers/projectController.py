from django.shortcuts import render,redirect
from metronus_app.forms.projectForm import ProjectForm
from metronus_app.model.project import Project,Company
from django.shortcuts import render_to_response, get_object_or_404
from metronus_app.common_utils import get_current_admin_or_403
from django.http import HttpResponseRedirect
from metronus_app.model.administrator import Administrator
from populate_database import basicLoad
from django.core.exceptions             import ObjectDoesNotExist, PermissionDenied
from django.http                        import HttpResponseForbidden
from django.contrib.auth import authenticate,login
from metronus_app.model.employee import Employee
from django.http import JsonResponse
from metronus_app.model.task import Task
from metronus_app.model.department import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.actor import Actor


def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del proyecto

    template:
    project_form.html
    """
     # Check that the user is logged in
    admin = get_current_admin_or_403(request)
    repeated_name=False
    error=False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            pname=form.cleaned_data['name']
            pro=findName(pname,admin)
            if pro is not None:
                if pro.deleted:
                    pro.deleted=False
                    pro.save()
                    return redirect('project_list')
                else:
                    repeated_name=True
            else:
                project = createProject(form,admin)
                return redirect('project_show', project_id=project.id)
        else:
            error = True
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProjectForm(initial={"project_id":0})

    return render(request, 'project/project_form.html',
                  {'form': form, 'repeated_name':repeated_name, 'error':error})

def createAsync(request):
    """
    parameters:
    form: el formulario con los datos del departamento

    returns:
    data: JSON con un mensaje de respuesta. Es un dict que contiene lo siguiente
    repeated_name: true si se ha repetido el nombre
    success:true si hubo exito, false si no

    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)

    data = {
        'repeated_name': False,
        'success':True
    }

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            pname=form.cleaned_data['name']
            pro=findName(pname,admin)
            if pro is not None:
                if pro.deleted:
                    pro.deleted = False
                    pro.save()
                    return JsonResponse(data)
                else:
                    data['repeated_name']=True
            else:
                project=createProject(form,admin)
                return JsonResponse(data)

    # if a GET (or any other method) we'll create a blank form
    else:
        return redirect('project_list')

    data['success']=False
    return JsonResponse(data)


def list(request):
    """
    returns:
    projectos: lista de proyectos de la compañía logeada

    template:
    project_list.html
    """
     # Check that the user is logged in
    lista=getListForRole(request)
    return render(request, "project/project_list.html", {"projects": lista})

def show(request,project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_manager = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__project_id=project, projectdepartmentemployeerole__role_id__name="Project manager").first()
    employees = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__project_id=project).distinct()
    tasks=Task.objects.filter(active=True, projectDepartment_id__project_id__id=project_id)
    departments = Department.objects.filter(active=True, projectdepartment__project_id__id=project_id)
    return render(request, "project/project_show.html", {"project": project, "employees": employees,"tasks":tasks, "departments": departments, "project_manager": project_manager})


def edit(request,project_id):
    """
    parameters/returns:
    form: el formulario con los datos del proyecto

    template:
    project_form.html
    """
     # Check that the user is logged in
    admin = get_current_admin_or_403(request)
    repeated_name=False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            project=get_object_or_404(Project,pk=form.cleaned_data['project_id'])
            if checkCompanyProject(project,admin.company_id):
                pro=findName(form.cleaned_data['name'],admin)
                #pro does not exists or it's the same
                if pro is None or pro.id==project.id:
                    updateProject(project,form)
                    return redirect('project_list')
                else:
                    if not pro.deleted:
                        repeated_name=True

    # if a GET (or any other method) we'll create a blank form
    else:
        project=get_object_or_404(Project,pk=project_id)
        form = ProjectForm(initial={"name":project.name,"project_id":project.id})


    return render(request, 'project/project_form.html', {'form': form, 'repeated_name':repeated_name})

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
    project=get_object_or_404(Project,pk=project_id)
    if checkCompanyProject(project,admin.company_id):
        deleteProject(project)

    return HttpResponseRedirect('/project/list')

#Auxiliar methods, containing the operation logic

def createProject(form, admin):
    pname=form.cleaned_data['name']
    company=admin.company_id
    return Project.objects.create(name=pname,deleted=False,company_id=company)

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
    res = project is not None and company_id==project.company_id and project.deleted==False
    if not res:
        raise PermissionDenied
    return res

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

def findName(pname,admin):
    return Project.objects.filter(name=pname,company_id=admin.company_id).first()

def getListForRole(request):
    actor=None
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

    if actor.user_type!='A':
        isTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name= "Team manager")
        res=isTeamManager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name__in=["Project manager","Coordinator"])
            res=roles.count()>0
            if not res:
                raise PermissionDenied
            else:
                projects=Project.objects.filter(projectdepartment__projectdepartmentemployeerole__employee_id=actor,
                    company_id=actor.company_id,deleted=False)
        else:
            projects=Project.objects.filter(company_id=actor.company_id,deleted=False)
    else:
        projects=Project.objects.filter(company_id=actor.company_id,deleted=False)

    return projects
