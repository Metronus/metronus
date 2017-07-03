from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, SuspiciousOperation
from django.db.models import Sum, F, FloatField
from metronus_app.forms.departmentForm import DepartmentForm
from metronus_app.model.department import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.employee import Employee
from metronus_app.model.actor import Actor
from metronus_app.model.task import Task
from metronus_app.model.timeLog import TimeLog
from datetime import date, timedelta, datetime
import re
from metronus_app.common_utils import (get_admin_executive_or_403,default_round,
    get_actor_or_403, is_executive,same_company_or_403, get_highest_role_tier)
from metronus_app.controllers.taskController import get_list_for_role as task_list
def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = get_admin_executive_or_403(request)
    repeated_name = False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            dname = form.cleaned_data['name']
            dep = find_name(dname, admin)
            if dep is not None:
                repeated_name = True
            else:
                department = create_department(form, admin)
                return HttpResponseRedirect('/department/view/'+str(department.id)+"/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DepartmentForm(initial={"department_id": 0, "name": ""})

    return render(request, 'department/department_form.html', {'form': form, 'repeated_name': repeated_name})


def create_async(request):
    """
    parameters:
    form: el formulario con los datos del departamento

    returns:
    data: JSON con un mensaje de respuesta. Es un dict que contiene lo siguiente
    repeated_name: true si se ha repetido el nombre
    success:true si hubo exito, false si no

    """

    # Check that the current user is an administrator
    admin = get_admin_executive_or_403(request)

    data = {
        'repeated_name': False,
        'success': True
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
            dname = form.cleaned_data['name']
            dep = find_name(dname, admin)
            if dep is not None:
                data['repeated_name'] = True
            else:
                create_department(form, admin)
                return JsonResponse(data)

    # if a GET (or any other method) we'll create a blank form
    else:
        return HttpResponseRedirect('/department/create')

    data['success'] = False
    return JsonResponse(data)

def list_departments(request):
    """
    returns:
    departments: lista de departamentos de la compañía logeada

    template:
    department_list.html
    """

    # Check that the current user has permissions
    lista = get_list_for_role(request)
    departments = lista.filter(active=True)
    deleted = lista.filter(active=False)
    return render(request, "department/department_list.html",
        {"departments": departments,"deleted":deleted})

def list_departments_search(request,name):
    """
    returns:
    departments: lista de departamentos de la compañía logeada

    template:
    department_list.html
    """

    # Check that the current user has permissions
    departments = get_list_for_role(request).filter(active=True)

    if name:
        departments.filter(name__icontains=name)

    return render(request, "department/department_search.html",
        {"departments": departments})

def view(request, department_id):
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
    actor=check_department(department, request)
    same_company_or_403(actor,department)

    coordinators = get_coordinator(department)
    # DO NOT ORDER the tasks, otherwise, by some random reason, it wont filter properly
    tasks = task_list(request).filter(projectDepartment_id__department_id=department).distinct()

    employees = Employee.objects.filter(user__is_active=True,
        projectdepartmentemployeerole__projectDepartment_id__department_id=department,
        projectdepartmentemployeerole__role_id__tier__lte=40).distinct().order_by("user__first_name", "user__last_name")

    return render(request, 'department/department_view.html', {'department': department, 'employees': employees,
                                                               'tasks': tasks, 'coordinators': coordinators})


def edit(request, department_id):
    """
    url = department/edit/(department_id)/

    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator or executive
    department = get_object_or_404(Department, pk=department_id)
    admin = get_admin_executive_or_403(request)
    same_company_or_403(admin,department)

    repeated_name = False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:


            dep = find_name(form.cleaned_data['name'], admin)
            # dep does not exists or it's the same
            if dep is None or dep.id == department.id:
                edit_department(department, form)
                return HttpResponseRedirect('/department/view/'+str(department.id)+"/")
            else:
                repeated_name = True
    # if a GET (or any other method) we'll create a blank form
    else:
        department = get_object_or_404(Department, pk=department_id)
        form = DepartmentForm(initial={"name": department.name, "department_id": department.id})

    return render(request, 'department/department_form.html', {'form': form, 'repeated_name': repeated_name})


def delete(request, department_id):
    """
    url = department/delete/(department_id)/
    parameters:
    department_id: the department id to delete

    returns:
    nothing

    template:
    deparment_list.html
    """
    department = get_object_or_404(Department, pk=department_id,active=True)
    # Check that the current user is an administrator or executive
    admin = get_admin_executive_or_403(request)
    same_company_or_403(admin,department)

    delete_department(department)

    return HttpResponseRedirect('/department/list')

def recover(request, department_id):
    """
    url = department/recover/(department_id)/
    parameters:
    department_id: the department id to recover

    returns:
    nothing

    template:
    deparment_list.html
    """
    department = get_object_or_404(Department, pk=department_id,active=False)
    # Check that the current user is an administrator or executive
    admin = get_admin_executive_or_403(request)
    same_company_or_403(admin,department)

    recover_department(department)

    return HttpResponseRedirect('/department/list')


##################################################################################################################
# Ajax methods for metric graphics
##################################################################################################################


def ajax_employees_per_task(request):
    """
    # Devuelve un objeto {'names': [tarea1, tarea2...], 'values': [tareas1, tareas2...]}

    # Parámetros obligatorios:
    # department_id - ID del departamento
    """
    if "department_id" not in request.GET:
        raise SuspiciousOperation

    department_id = request.GET["department_id"]

    department = get_object_or_404(Department, pk=department_id)
    actor=check_department(department, request)
    same_company_or_403(actor,department)

    dpmt_tasks = Task.objects.filter(active=True, projectDepartment_id__department_id__id=department_id)

    data = {
        'names': [],
        'values': []
    }

    for task in dpmt_tasks:
        data['names'].append(task.name)
        data['values'].append(TimeLog.objects.filter(task_id=task).distinct('employee_id').count())

    return JsonResponse(data)


def ajax_time_per_task(request):
    """
    # Devuelve un objeto {'names': [tarea1, tarea2...], 'values': [tiempo1, tiempo2...]}

    # Parámetros obligatorios:
    # department_id - ID del departamento

    # Parámetros opcionales:
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +02:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request
    """
    if "department_id" not in request.GET:
        raise SuspiciousOperation

    department_id = request.GET["department_id"]

    department = get_object_or_404(Department, pk=department_id)
    actor=check_department(department, request)
    same_company_or_403(actor,department)


    # Get and parse the dates and the offset
    start_date = request.GET.get("start_date", str(date.today() - timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
    date_regex = re.compile("^\d{4}-\d{2}-\d{2}$")

    if date_regex.match(start_date) is None or date_regex.match(end_date) is None:
        raise SuspiciousOperation("Start/end date are not valid")

    offset = request.GET.get("offset", "+00:00")
    offset_regex = re.compile("^(\+|-)\d{2}:\d{2}$")

    if offset_regex.match(offset) is None:
        raise SuspiciousOperation("Time offset is not valid")

    # Append time offsets
    start_date += " 00:00" + offset
    end_date += " 00:00" + offset

    dpmt_tasks = Task.objects.filter(active=True, projectDepartment_id__department_id__id=department_id)

    data = {
        'names': [],
        'values': []
    }

    for task in dpmt_tasks:
        time_total = TimeLog.objects.filter(
            task_id=task,
            workDate__range=[start_date, end_date]).aggregate(Sum('duration'))["duration__sum"]

        if time_total is None:
            time_total = 0

        data['names'].append(task.name)
        data['values'].append(time_total)

    return JsonResponse(data)


def ajax_profit_per_date(request, department_id):
    """
    # url = department/ajax_profit_per_date/<department_id>
    # Devuelve un objeto con las fechas y las rentabilidades diarias y acumuladas
    #

    # Parámetro obligatorio:
    ninguno

    # Parámetros opcionales:
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    #Ejemplo
    #/department/ajaxAcumProfit/1/

    #devuelve lo siguiente
    #{"acumExpenses": [0, 1457.18015695298, 3071.32603956358, 4438.9463044226895, 6465.819587171869, 7912.658013249849, 9791.46399488711, 11615.32872003681, 13494.726436052111, 15102.72092592163, 16718.442225021892, 18327.93613617256, 20841.87940297534, 22953.949544558982, 24314.625169466122, 25683.231076691303, 27287.16055422502, 28760.84364198999, 31104.25163724206, 32808.89759982555, 34747.27999087272, 36150.9847742294, 37523.6098087571, 38600.05927001698, 40953.76583717958, 42469.88703139726, 44081.49130458021, 45420.3135021882, 47945.57927018715, 49368.262834629466, 51133.932803674485],
    "acumIncome": [0, 155861.848663544, 262457.90948135697, 396454.85575838294, 572637.4741922909, 703418.0032829699, 889130.2419483919, 1057821.248373874, 1259349.275922576, 1393310.956579081, 1539441.608896949, 1700420.3827038072, 1955067.034572835, 2187486.6539142523, 2300530.309442004, 2429378.038836404, 2615789.2939997134, 2742614.2371285204, 3004214.3219032744, 3205025.4834073624, 3363963.7766520614, 3552325.908039063, 3718850.184141958, 3833661.86021891, 4044009.6991582112, 4159278.365569177, 4285423.634163346, 4417334.086840815, 4692230.750316469, 4819759.243153938, 4997733.5628708275],
    "dates": ["2017-03-21", "2017-03-22", "2017-03-23", "2017-03-24", "2017-03-25", "2017-03-26", "2017-03-27", "2017-03-28", "2017-03-29", "2017-03-30", "2017-03-31", "2017-04-01", "2017-04-02", "2017-04-03", "2017-04-04", "2017-04-05", "2017-04-06", "2017-04-07", "2017-04-08", "2017-04-09", "2017-04-10", "2017-04-11", "2017-04-12", "2017-04-13", "2017-04-14", "2017-04-15", "2017-04-16", "2017-04-17", "2017-04-18", "2017-04-19", "2017-04-20"],
    "income": [0, 155861.848663544, 106596.060817813, 133996.946277026, 176182.618433908, 130780.529090679, 185712.238665422, 168691.006425482, 201528.027548702, 133961.680656505, 146130.652317868, 160978.773806858, 254646.651869028, 232419.619341417, 113043.655527752, 128847.7293944, 186411.255163309, 126824.943128807, 261600.084774754, 200811.161504088, 158938.293244699, 188362.131387002, 166524.276102895, 114811.676076952, 210347.838939301, 115268.666410966, 126145.268594169, 131910.452677469, 274896.663475654, 127528.492837469, 177974.319716889],
    "expenses": [0, 1457.18015695298, 1614.1458826106, 1367.62026485911, 2026.87328274918, 1446.83842607798, 1878.80598163726, 1823.8647251497, 1879.3977160153, 1607.99448986952, 1615.72129910026, 1609.49391115067, 2513.94326680278, 2112.07014158364, 1360.67562490714, 1368.60590722518, 1603.92947753372, 1473.68308776497, 2343.40799525207, 1704.64596258349, 1938.38239104717, 1403.70478335668, 1372.6250345277, 1076.44946125988, 2353.7065671626, 1516.12119421768, 1611.60427318295, 1338.82219760799, 2525.26576799895, 1422.68356444232, 1765.66996904502]}  "expected_productivity": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 4.0, 4.0, 2.0, 2.0, 2.0]}}
    """

    department = get_object_or_404(Department, pk=department_id)
    actor=check_department(department, request)
    same_company_or_403(actor,department)

    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today() - timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
    date_regex = re.compile("^\d{4}-\d{2}-\d{2}$")

    if date_regex.match(start_date) is None or date_regex.match(end_date) is None:
        raise SuspiciousOperation("Start/end date are not valid")

    offset = request.GET.get("offset", "+00:00")
    offset_regex = re.compile("^(\+|-)\d{2}:\d{2}$")

    if offset_regex.match(offset) is None:
        raise SuspiciousOperation("Time offset is not valid")

    # Append time offsets
    start_date += " 00:00" + offset
    end_date += " 00:00" + offset

    # Get all dates between start and end
    dates = []
    str_dates = []

    d1 = datetime.strptime(start_date[0:19]+start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19]+end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1         # timedelta
    for i in range(delta.days + 1):
        str_dates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))

    data = {'dates': str_dates, 'expenses': [], 'income': [], 'acumExpenses': [], 'acumIncome': []}

    # Profit
    # for each date, we will find all logs, calculate the sum and acumulate it
    index = 0
    for log_date in dates:
        logs = TimeLog.objects.filter(task_id__projectDepartment_id__department_id_id=department_id,
                                      workDate__year=log_date.year, workDate__month=log_date.month,
                                      workDate__day=log_date.day).distinct()
        expenses = logs.aggregate(total_expenses=Sum(F("duration")/60.0*F("employee_id__price_per_hour"), output_field=FloatField()))["total_expenses"]
        expenses = expenses if expenses is not None else 0
        income = logs.aggregate(total_income=Sum(F("task_id__price_per_unit")*F("produced_units")))["total_income"]
        income = income if income is not None else 0

        data['expenses'].append(default_round(expenses))
        data['income'].append(default_round(income))
        if index == 0:
            data['acumExpenses'].append(default_round(expenses))
            data['acumIncome'].append(default_round(income))
        else:
            data['acumExpenses'].append(default_round(data['acumExpenses'][index-1]+expenses))
            data['acumIncome'].append(default_round(data['acumIncome'][index-1]+income))
        index += 1
    return JsonResponse(data)

def validate_name_ajax(request):
    """
    checks whether the department name is unique
    """
    name = request.GET.get("name")
    is_taken = name and Department.objects.filter(name=name).exists()
    return JsonResponse({'is_taken': is_taken})


##################################################################################################################
# Auxiliar methods, containing the operation logic
##################################################################################################################


def find_name(dname, admin):
    """Finds a department with the specified name in the company, as it must be unique"""
    return Department.objects.filter(name=dname, company_id=admin.company_id).first()


def create_department(form, admin):
    """Creates a department supposing the data in the form is OK"""
    dname = form.cleaned_data['name']
    company = admin.company_id
    return Department.objects.create(name=dname, active=True, company_id=company)


def edit_department(department, form):
    """Edits a department supposing the data in the form is OK"""
    department.name = form.cleaned_data['name']
    department.save()


def delete_department(department):
    """Deletes a department"""
    department.active = False
    department.save()

def recover_department(department):
    """Recover a department"""
    department.active = True
    department.save()


def check_department(department, request):
    """
    checks if the department belongs to the logged actor with appropiate roles
    Admin, manager or project manager
    """

    actor=get_actor_or_403(request)
    highest=get_highest_role_tier(actor)
    if highest>=50:
        # Admins and executives can do everything
        return actor
    elif not department.active:
        raise PermissionDenied
    elif ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
        projectDepartment_id__department_id=department,
        role_id__tier__gte=20).exists():
        # If it's for view, coordinators and greater can access too
        return actor

    # Otherwise GTFO
    raise PermissionDenied


def get_list_for_role(request):
    """
    Gets the list of departments according to the role tier of the logged user
    """
    actor=get_actor_or_403(request)

    # Admins and executives can do everything

    if actor.user_type == "A" or is_executive(actor):
        return Department.objects.filter(company_id=actor.company_id).distinct().order_by("name")

    # If it's for view, coordinators and greater can access too
    if ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
        role_id__tier__gte=20).exists():

        return Department.objects.filter(
                projectdepartment__projectdepartmentemployeerole__employee_id=actor,
                projectdepartment__projectdepartmentemployeerole__role_id__tier__gte=20,
                company_id=actor.company_id,active=True).distinct().order_by("name")

    # Otherwise GTFO
    raise PermissionDenied


def get_coordinator(department):
    """
    Gets the coordinators from a department
    """
    return Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__department_id=department,
                                   projectdepartmentemployeerole__role_id__tier=20).distinct().order_by("user__first_name","user__last_name")
