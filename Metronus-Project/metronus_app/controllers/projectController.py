from django.shortcuts                                   import render_to_response, get_object_or_404, render,redirect
from django.core.exceptions                             import ObjectDoesNotExist, PermissionDenied
from django.http                                        import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.contrib.auth                                import authenticate,login
from django.db.models                                   import Sum

from metronus_app.forms.projectForm                     import ProjectForm
from metronus_app.model.project                         import Project,Company
from metronus_app.common_utils                          import get_current_admin_or_403
from metronus_app.model.administrator                   import Administrator
from metronus_app.model.employee                        import Employee
from metronus_app.model.task                            import Task
from metronus_app.model.timeLog                         import TimeLog
from metronus_app.model.department                      import Department
from metronus_app.model.projectDepartmentEmployeeRole   import ProjectDepartmentEmployeeRole
from metronus_app.model.actor                           import Actor

from datetime                                           import date, timedelta

import re


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
                return redirect('project_view', project_id=project.id)
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
    project_manager = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__project_id=project, projectdepartmentemployeerole__role_id__tier__gte=40).first()
    employees = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__project_id=project).distinct()
    tasks=Task.objects.filter(active=True, projectDepartment_id__project_id__id=project_id)
    departments = Department.objects.filter(active=True, projectdepartment__project_id__id=project_id)
    return render(request, "project/project_view.html", {"project": project, "employees": employees,"tasks":tasks, "departments": departments, "project_manager": project_manager})


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

############################################################################
### Ajax methods for metric graphics
############################################################################

def ajax_employees_per_department(request):
    """
    # Devuelve un objeto {'names': [dpto1, dpto2...], 'values': [empleados1, empleados2...]}

    # Parámetros obligatorios:
    # project_id - ID del proyecto
    """
    if "project_id" not in request.GET:
        return HttpResponseBadRequest()

    project_id = request.GET["project_id"]
    check_metrics_authorized_for_project(request.user, project_id)

    logged = request.user.actor
    company_departments = Department.objects.filter(active=True, company_id=logged.company_id)

    # The first method checks that the project is fine
    project = Project.objects.get(id=project_id)

    data = {'names': [], 'values': []}

    for dpmt in company_departments:
        data['names'].append(dpmt.name)
        data['values'].append(ProjectDepartmentEmployeeRole.objects.filter(projectDepartment_id__project_id=project, projectDepartment_id__department_id=dpmt).count())

    return JsonResponse(data)

def ajax_tasks_per_department(request):
    """
    # Devuelve un objeto {'names': [dpto1, dpto2...], 'values': [tareas1, tareas2...]}

    # Parámetros obligatorios:
    # project_id - ID del proyecto
    """

    if "project_id" not in request.GET:
        return HttpResponseBadRequest()

    project_id = request.GET["project_id"]
    check_metrics_authorized_for_project(request.user, project_id)

    logged = request.user.actor
    company_departments = Department.objects.filter(active=True, company_id=logged.company_id)

    # The first method checks that the project is fine
    project = Project.objects.get(id=project_id)

    data = {'names': [], 'values': []}

    for dpmt in company_departments:
        data['names'].append(dpmt.name)
        data['values'].append(Task.objects.filter(projectDepartment_id__project_id=project, projectDepartment_id__department_id=dpmt).count())

    return JsonResponse(data)

def ajax_time_per_department(request):
    """
    # Devuelve un objeto {'names': [dpto1, dpto2...], 'values': [tiempo1, tiempo2...]}

    # Parámetros obligatorios:
    # project_id - ID del proyecto

    # Parámetros opcionales: 
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    """
    if "project_id" not in request.GET:
        return HttpResponseBadRequest()

    project_id = request.GET["project_id"]
    check_metrics_authorized_for_project(request.user, project_id)

    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today()- timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today() ))
    date_regex = re.compile("^\d{4}-\d{2}-\d{2}$")

    if date_regex.match(start_date) is None or date_regex.match(end_date) is None:
        return HttpResponseBadRequest("Start/end date are not valid")

    offset = request.GET.get("offset", "+00:00")
    offset_regex = re.compile("^(\+|-)\d{2}:\d{2}$")

    if offset_regex.match(offset) is None:
        return HttpResponseBadRequest("Time offset is not valid")

    # Append time offsets
    start_date += " 00:00" + offset
    end_date += " 00:00" + offset

    logged = request.user.actor
    company_departments = Department.objects.filter(active=True, company_id=logged.company_id)

    # The first method checks that the project is fine
    project = Project.objects.get(id=project_id)

    data = {'names': [], 'values': []}

    for dpmt in company_departments:
        time_total = TimeLog.objects.filter(task_id__projectDepartment_id__project_id=project, task_id__projectDepartment_id__department_id=dpmt,
                                                           workDate__range=[start_date, end_date]).aggregate(Sum('duration'))["duration__sum"]
        if time_total is None: 
            time_total = 0

        data['names'].append(dpmt.name)
        data['values'].append(time_total)

    return JsonResponse(data)


##################################################################################################################
#Auxiliar methods, containing the operation logic
##################################################################################################################

def check_metrics_authorized_for_project(user, project_id):
    """ Raises 403 if the current actor is not allowed to obtain metrics for the project"""
    if not user.is_authenticated():
        raise PermissionDenied

    project = get_object_or_404(Project, deleted=False, id=project_id)
    logged = user.actor

    # Check that the companies match
    if logged.company_id != project.company_id:
        raise PermissionDenied

    if logged.user_type == 'E':
        # If it's not an admin, check that it has role EXECUTIVE (50) or higher
        try:
            ProjectDepartmentEmployeeRole.objects.get(employee_id=logged, role_id__tier__gte=50, projectDepartment_id__project_id=project)
        except ObjectDoesNotExist:
            raise PermissionDenied

def createProject(form, admin):
    """Creates a new project supposing the data in the form is OK"""
    pname=form.cleaned_data['name']
    company=admin.company_id
    return Project.objects.create(name=pname,deleted=False,company_id=company)

def updateProject(project,form):
    """Edits a  project supposing the data in the form is OK"""
    project.name = form.cleaned_data['name']
    project.save()

def deleteProject(project):
    """Deletes a project"""
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
    """ Finds a project with the specified name in the company, as it must be unique"""
    return Project.objects.filter(name=pname,company_id=admin.company_id).first()

def getListForRole(request):
    """Gets the list of projects visible to the logged user, as it depends on their roles"""
    actor=None
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

    if actor.user_type!='A':
        is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=is_team_manager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier__in=[50,40,20])
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
