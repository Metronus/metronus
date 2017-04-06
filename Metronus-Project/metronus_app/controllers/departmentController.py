from django.shortcuts                                   import render, get_object_or_404
from django.http                                        import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.exceptions                             import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth                                import authenticate,login
from django.db.models                                   import Sum

from metronus_app.forms.departmentForm                  import DepartmentForm
from metronus_app.model.department                      import Department
from metronus_app.model.projectDepartmentEmployeeRole   import ProjectDepartmentEmployeeRole
from metronus_app.model.employee                        import Employee
from metronus_app.model.actor                           import Actor
from metronus_app.model.task                            import Task
from metronus_app.model.timeLog                         import TimeLog
from metronus_app.model.administrator                   import Administrator
from metronus_app.common_utils                          import get_current_admin_or_403,get_current_employee_or_403

from populate_database                                  import basicLoad
from datetime                                           import date, timedelta

import re

def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = checkDepartment(None,request)
    repeated_name=False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            dname=form.cleaned_data['name']
            dep=findName(dname,admin)
            if dep is not None:
                if not dep.active:
                    dep.active=True
                    dep.save()
                    return HttpResponseRedirect('/department/view/'+str(dep.id)+"/")
                else:
                    repeated_name=True
            else:
                department=createDepartment(form,admin)
                return HttpResponseRedirect('/department/view/'+str(department.id)+"/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DepartmentForm(initial={"department_id":0,"name":""})


    return render(request, 'department/department_form.html', {'form': form,'repeated_name':repeated_name})

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
    admin = checkDepartment(None,request)

    data = {
        'repeated_name': False,
        'success':True
    }

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            dname=form.cleaned_data['name']
            dep=findName(dname,admin)
            if dep is not None:
                if not dep.active:
                    dep.active=True
                    dep.save()
                    return JsonResponse(data)
                else:
                    data['repeated_name']=True
            else:
                department=createDepartment(form,admin)
                return JsonResponse(data)

    # if a GET (or any other method) we'll create a blank form
    else:
        return HttpResponseRedirect('/department/create')

    data['success']=False
    return JsonResponse(data)


def list(request):

    """
    returns:
    departments: lista de departamentos de la compañía logeada

    template:
    department_list.html
    """

    # Check that the current user has permissions
    lista=getListForRole(request)
    return render(request, "department/department_list.html", {"departments": lista})

def view(request,department_id):
    """
    url = department/view/(department_id)/

    parameters:
    department_id: id del department

    returns:
    department: datos del departamento
    employees: objetos Empleados
    tasks: lista de tareas del departamento

    template: department_view.html
    """
    department = get_object_or_404(Department, pk=department_id)
    admin = checkDepartmentForView(department,request,True)

    coordinator=get_coordinator(department)
    tasks=Task.objects.filter(active=True, projectDepartment_id__department_id__id=department_id)
    employees = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__department_id=department).distinct()
    
    return render(request, 'department/department_view.html', {'department': department, 'employees': employees,
        'tasks':tasks,'coordinator':coordinator})

def edit(request,department_id):
    """
    url = department/edit/(department_id)/

    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = checkDepartment(None,request)
    repeated_name=False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            department=get_object_or_404(Department,pk=form.cleaned_data['department_id'])
           
            dep=findName(form.cleaned_data['name'],admin)
            #dep does not exists or it's the same
            if dep is None or dep.id==department.id:
                editDepartment(department,form)
                return HttpResponseRedirect('/department/view/'+str(department.id)+"/")
            else:
                if dep.active:
                    repeated_name=True
    # if a GET (or any other method) we'll create a blank form
    else:

        department=get_object_or_404(Department,pk=department_id)
        form = DepartmentForm(initial={"name":department.name,"department_id":department.id})


    return render(request, 'department/department_form.html', {'form': form,'repeated_name':repeated_name})

def delete(request,department_id):
    """
    url = department/delete/(department_id)/
    parameters:
    department_id: the department id to delete

    returns:
    nothing

    template:
    deparment_list.html
    """
    department=get_object_or_404(Department,pk=department_id)
    
    # Check that the current user is an administrator
    admin = checkDepartment(department,request)    
    deleteDepartment(department)

    return HttpResponseRedirect('/department/list')

##################################################################################################################
### Ajax methods for metric graphics
##################################################################################################################

def ajax_employees_per_task(request):
    # Devuelve un objeto {'names': [tarea1, tarea2...], 'values': [tareas1, tareas2...]}

    # Parámetros obligatorios:
    # department_id - ID del departamento

    if "department_id" not in request.GET:
        return HttpResponseBadRequest()

    department_id = request.GET["department_id"]
    check_metrics_authorized_for_department(request.user, department_id)

    logged = request.user.actor
    dpmt_tasks = Task.objects.filter(active = True, projectDepartment_id__department_id__id = department_id)

    data = {
        'names' : [],
        'values' : []
    }

    for task in dpmt_tasks:
        data['names'].append(task.name)
        data['values'].append(TimeLog.objects.filter(task_id = task).distinct('employee_id').count())

    return JsonResponse(data)

def ajax_time_per_task(request):
    # Devuelve un objeto {'names': [tarea1, tarea2...], 'values': [tiempo1, tiempo2...]}

    # Parámetros obligatorios:
    # department_id - ID del departamento

    # Parámetros opcionales: 
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +02:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    if "department_id" not in request.GET:
        return HttpResponseBadRequest()

    department_id = request.GET["department_id"]
    check_metrics_authorized_for_department(request.user, department_id)

    # Get and parse the dates and the offset
    start_date = request.GET.get("start_date", str(date.today()))
    end_date = request.GET.get("end_date", str(date.today() - timedelta(days=30)))
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
    dpmt_tasks = Task.objects.filter(active = True, projectDepartment_id__department_id__id = department_id)

    data = {
        'names' : [],
        'values' : []
    }

    for task in dpmt_tasks:
        time_total = TimeLog.objects.filter(task_id = task, workDate__range = [start_date, end_date]).aggregate(Sum('duration'))["duration__sum"]

        if time_total is None: 
            time_total = 0

        data['names'].append(task.name)
        data['values'].append(time_total)

    return JsonResponse(data)


##################################################################################################################
#Auxiliar methods, containing the operation logic
##################################################################################################################

def check_metrics_authorized_for_department(user, dpmt_id):
    # Raises 403 if the current actor is not allowed to obtain metrics for the project
    if not user.is_authenticated():
        raise PermissionDenied

    department = get_object_or_404(Department, active=True, id=dpmt_id)
    logged = user.actor

    # Check that the companies match
    if logged.company_id != department.company_id:
        raise PermissionDenied

    if logged.user_type == 'E':
        # If it's not an admin, check that it has role EXECUTIVE (50) or higher for any project in the department
        try:
            ProjectDepartmentEmployeeRole.objects.get(employee_id=logged, role_id__tier__gte=50, projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            raise PermissionDenied

def findName(dname,admin):
    return Department.objects.filter(name=dname,company_id=admin.company_id).first()

def createDepartment(form,admin):

    dname=form.cleaned_data['name']
    company=admin.company_id
    return Department.objects.create(name=dname,active=True,company_id=company)

def editDepartment(department,form):
    department.name = form.cleaned_data['name']
    department.save()

def deleteDepartment(department):
    department.active=False
    department.save()

def checkDepartment(dep,request):
    """
    this check department is only for creating, modifying or deleting
    """
    return checkDepartmentForView(dep,request,False)
def checkDepartmentForView(dep,request,forView):
    """
    checks if the department belongs to the logged actor with appropiate roles
    Admin, manager or project manager
    if forView is true, the coordinator has access too
    """
    actor=None
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

    # Check that the actor has permission to view the dep
    if dep is not None and (dep.company_id != actor.company_id or not dep.active):
        raise PermissionDenied

    if actor.user_type!='A':
        isTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=isTeamManager.count()>0

        if not res:
            if forView:
                roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                         role_id__tier__in=[50,40,20])
            else:
                roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                        role_id__tier__gte=40)
            res=roles.count()>0
        if not res:
            raise PermissionDenied

    return actor

def checkCompanyDepartmentSession(department,admin):
    """
    checks if the department belongs to the logged company
    """
    return checkCompanyDepartment(department,admin.company_id)

def checkCompanyDepartment(department,company_id):
    """
    checks if the department belongs to the specified company
    """
    res= department is not None and company_id==department.company_id 
    if not res:
        raise PermissionDenied
    return res

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
                    role_id__tier= 30)
        res=isTeamManager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier__in=[50,40,20])
            res=roles.count()>0
            if not res:
                raise PermissionDenied
            else:
                departments=Department.objects.filter(projectdepartment__projectdepartmentemployeerole__employee_id=actor,
                    company_id=actor.company_id,active=True)
        else:
            departments=Department.objects.filter(company_id=actor.company_id,active=True)
    else:
        departments=Department.objects.filter(company_id=actor.company_id,active=True)

    return departments 

def get_coordinator(department):
    return Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__department_id=department,
        projectdepartmentemployeerole__role_id__tier=20).first()