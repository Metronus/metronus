from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy
from django.db.models import Sum, F, FloatField
from django.contrib.auth.decorators import login_required

from metronus_app.forms.employeeRegisterForm import EmployeeRegisterForm
from metronus_app.forms.employeeEditForm import EmployeeEditForm
from metronus_app.forms.employeePasswordForm import EmployeePasswordForm
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.employeeLog import EmployeeLog
from metronus_app.model.task import Task
from metronus_app.model.goalEvolution import GoalEvolution
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.core import serializers
from django.http import HttpResponse

from metronus_app.common_utils import (get_current_admin_or_403, check_image, get_current_employee_or_403, send_mail,
                                       is_email_unique, is_username_unique)
from datetime import date, timedelta, datetime
import re


def create(request):
    """
    parameters:
        redirect: opcional, incluir en la URL de la petición si se quiere redirigir a la página del empleado creado
    returns:
        form: formulario con los datos necesarios para el registro del empleado
        success: opcional, si se ha tenido éxito al crear un empleado
        errors: opcional, array de mensajes de error si ha habido algún error

    errores: (todos empiezan por employeeCreation_)
        passwordsDontMatch: las contraseñas no coinciden
        usernameNotUnique: el nombre de usuario ya existe
        imageNotValid: la imagen no es válida por formato y/o tamaño
        formNotValid: el formulario contiene errores
        priceNotValid: el precio debe ser mayor que 0
        emailNotUnique:si el correo no es úinco

    template:
        employee_register.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    # If it's a GET request, return an empty form
    if request.method == "GET":
        return render(request, 'employee/employee_register.html', {'form': EmployeeRegisterForm()})

    elif request.method == "POST":
        # We are serving a POST request
        form = EmployeeRegisterForm(request.POST, request.FILES)

        if form.is_valid():

            errors = []

            # Check that the passwords match
            if not check_passwords(form):
                errors.append('employeeCreation_passwordsDontMatch')

            # Check that the username is unique
            if not is_username_unique(form.cleaned_data["username"]):
                errors.append('employeeCreation_usernameNotUnique')

            # Check that the email is unique
            if not is_email_unique(form.cleaned_data["email"]):
                errors.append('employeeCreation_emailNotUnique')

            # Check that the image is OK
            if not check_image(form, 'photo'):
                errors.append('employeeCreation_imageNotValid')

            # Check that the price is OK
            if form.cleaned_data['price_per_hour'] <= 0:
                errors.append('employeeCreation_priceNotValid')

            if not errors:
                # Everything is OK, create the employee
                employee_user = create_employee_user(form)
                employee = create_employee(employee_user, admin, form)
                EmployeeLog.objects.create(employee_id=employee, event="A", price_per_hour=employee.price_per_hour)
                send_register_email(form.cleaned_data["email"], form.cleaned_data["first_name"])

                if "redirect" in request.GET:  # Redirect to the created employee
                    return HttpResponseRedirect('/employee/view/' + form.cleaned_data["username"] + '/')
                else:  # Return a new form
                    return render(request, 'employee/employee_register.html',
                                  {'form': EmployeeRegisterForm(), 'success': True})
            else:
                # There are errors
                return render(request, 'employee/employee_register.html', {'form': form, 'errors': errors})

        # Form is not valid
        else:
            return render(request, 'employee/employee_register.html',
                          {'form': form, 'errors': ['employeeCreation_formNotValid']})
    else:
        # Another request method
        raise PermissionDenied


def list_employees(request):
    """
    parameters/returns:
    employees: lista de objetos employee a los que tiene acceso el administrador (los que están en su empresa)

    template: employee_list.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    employees = Employee.objects.filter(company_id=admin.company_id, user__is_active=True)
    return render(request, 'employee/employee_list.html', {'employees': employees})


def view(request, username):
    """
    url = employee/view/<username>

    parameters/returns:
    employee: datos del empleado
    employee_roles: objetos ProjectDepartmentEmployeeRole (bibah) con todos los roles del empleado

    template: employee_view.html
    """

    # Check that the user is logged in and it's an administrator
    try:
        logged = get_current_admin_or_403(request)
    except PermissionDenied:
        logged = get_current_employee_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check that the admin has permission to view that employee
    if employee.company_id != logged.company_id:
        raise PermissionDenied

    employee_roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee)

    #Check the logged's roles are greater than this for at least one project
    if logged.user_type=="E":
        my_roles=ProjectDepartmentEmployeeRole.objects.filter(employee_id=logged)
        authorized=my_roles.exists()
        if authorized:
            for role in my_roles: 
                if ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                    projectDepartment_id=role.projectDepartment_id,tier__lt=role.tier).exists():
                    authorized=True
                    break

        if not authorized:
            raise PermissionDenied
    return render(request, 'employee/employee_view.html', {'employee': employee, 'employee_roles': employee_roles})


def edit(request, username):
    """
    url = employee/edit/<username>

    parameters/returns:
        form: formulario de edicion de datos de empleado

    errors:
        'employeeCreation_formNotValid': si el formulario no es válido

    template: employee_edit.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check that the admin has permission to view that employee
    if employee.company_id != admin.company_id:
        raise PermissionDenied

    if request.method == "GET":
        # Return a form filled with the employee's data
        form = EmployeeEditForm(initial={
            'first_name': employee.user.first_name,
            'last_name': employee.user.last_name,
            'email': employee.user.email,
            'identifier': employee.identifier,
            'phone': employee.phone,
            'price_per_hour': employee.price_per_hour
        })

        return render(request, 'employee/employee_edit.html', {'form': form})

    elif request.method == "POST":
        # Process the received form

        form = EmployeeEditForm(request.POST)
        if form.is_valid():
            errors = []
            # Check that the price is OK
            if form.cleaned_data['price_per_hour'] <= 0:
                errors.append('employeeCreation_priceNotValid')
            if not errors:
                # Update employee data
                employee.identifier = form.cleaned_data["identifier"]
                employee.phone = form.cleaned_data["phone"]
                # New log if the salary has changed
                new_log = employee.price_per_hour != form.cleaned_data["price_per_hour"]

                employee.price_per_hour = form.cleaned_data["price_per_hour"]

                # Update user data
                user = employee.user
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.email = form.cleaned_data["email"]

                user.save()
                employee.save()

                # New log if the salary has changed
                if new_log:
                    EmployeeLog.objects.create(employee_id=employee, event="C",
                                               price_per_hour=form.cleaned_data["price_per_hour"])
                return HttpResponseRedirect('/employee/view/' + username + '/')
            else:
                # There are errors
                return render(request, 'employee/employee_edit.html', {'form': form, 'errors': errors})

        else:
            # Form is not valid
            return render(request, 'employee/employee_edit.html', {'form': form,
                                                                   'errors': ['employeeCreation_formNotValid']})
    else:
        raise PermissionDenied


def update_password(request, username):
    """
    url = employee/updatePassword/<username>

    parameters:
        password1: contraseña a establecer
        password2: repetición de la contraseña

    returns:
        {'success': true/false: 'errors': [...]}

    errors:
        'employeeCreation_formNotValid': si el formulario no es válido
        'employeeCreation_passwordsDontMatch' : si las contraseñas no coinciden

    template: ninguna (ajax)
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check that the admin has permission to view that employee
    if employee.company_id != admin.company_id:
        raise PermissionDenied

    if request.method == 'POST':
        # Process the form
        form = EmployeePasswordForm(request.POST)

        if form.is_valid():
            pass1 = form.cleaned_data["password1"]
            pass2 = form.cleaned_data["password2"]

            if pass1 != pass2:
                return JsonResponse({'success': False, 'errors': ['employeeCreation_passwordsDontMatch']})

            user = employee.user
            user.set_password(pass1)
            user.save()
            notify_password_change(user.email, user.first_name)

            return JsonResponse({'success': True, 'errors': []})
        else:
            # Invalid form
            return JsonResponse({'success': False, 'errors': ['employeeCreation_formNotValid']})


def delete(request, username):
    """
    url = employee/delete/<username>

    parameters/returns:
    Nada, redirecciona a la vista de listado de empleados

    template: ninguna
    """

    admin = get_current_admin_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check that the admin has permission to edit that employee
    if employee.company_id != admin.company_id:
        raise PermissionDenied

    employee_user = employee.user
    employee_user.is_active = False
    employee_user.save()

    EmployeeLog.objects.create(employee_id=employee, event="B", price_per_hour=employee.price_per_hour)
    return HttpResponseRedirect('/employee/list')


# AJAX methods
@login_required
def ajax_productivity_per_task(request, username):
    """
    # url = employee/ajax_productivity_per_task/<username>
    # Devuelve un objeto cuyas claves son las ID de los proyectos y sus valores un objeto
    #{'name': ..., 'total_productivity': X,'expected_productivity':Y} (X e Y en unidades goal_description/hora)

    #Ejemplo:
    #/employee/ajax_productivity_per_task/JoseGavilan

    #devuelve lo siguiente
    #{"3": {"total_productivity": 0.7125, "expected_productivity": 2.0, "name": "Hacer cosas de front"}}
    """
    # Check that the user is logged in and it's an administrator or with permissions
    try:
        logged = get_current_admin_or_403(request)
    except PermissionDenied:
        logged = get_current_employee_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check the company is the same for logged and the searched employee
    if employee.company_id != logged.company_id:
        raise PermissionDenied

    # Find tasks with timelog in date range and annotate the sum of the production and time
    tasks = Task.objects.filter(active=True, projectDepartment_id__projectdepartmentemployeerole__employee_id=employee,
                                production_goal__isnull=False).distinct().annotate(total_produced_units=Sum("timelog__produced_units"), total_duration=Sum("timelog__duration"))
    data = {}
    # Save productivity for each task
    for task in tasks:

        total_produced_units = task.total_produced_units
        total_duration = task.total_duration
        if total_duration is None or total_produced_units is None or total_duration == 0:
            total_productivity = 0
        else:
            # Duration is in minutes,so we multiply by 60 (duration is in the denominator)
            total_productivity = 60*total_produced_units/total_duration

        data[task.id] = {
                            'name': task.name,
                            'expected_productivity': task.production_goal,
                            'total_productivity': total_productivity
                        }

    return JsonResponse(data)

@login_required
def ajax_productivity_per_task_and_date(request, username):
    """
    # url = employee/ajax_productivity_per_task/<username>
    # Devuelve un objeto con las fechas y las productividades de la tarea real y esperada
    #{'name': ..., 'total_productivity': X,'expected_productivity':Y} (X en unidades goal_description/hora)

    # Parámetro obligatorio:
    # task_id: el id de la tarea en cuestión

    # Parámetros opcionales:
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    #Ejemplo
    #/employee/ajax_productivity_per_task_and_date/JoseGavilan?task_id=3&start_date=2017-02-05&end_date=2017-02-16

    #devuelve lo siguiente
    #{"dates":
    #   ["2017-02-05", "2017-02-06", "2017-02-07", "2017-02-08", "2017-02-09", "2017-02-10", "2017-02-11", "2017-02-12", "2017-02-13", "2017-02-14", "2017-02-15", "2017-02-16"],
    #"task": {"name": "Hacer cosas de front",
    #   "real_productivity": [0, 0, 0, 0, 0, 0, 0, 1.2, 0, 0.225, 0, 0],
    #   "task_id": 3,
    #   "expected_productivity": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 4.0, 4.0, 2.0, 2.0, 2.0]}}
    """

    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today() - timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
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

    # Check that the user is logged in and it's an administrator or with permissions
    try:
        logged = get_current_admin_or_403(request)
    except PermissionDenied:
        logged = get_current_employee_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check the company is the same for logged and the searched employee
    if employee.company_id != logged.company_id:
        raise PermissionDenied

    task_id = request.GET.get("task_id")
    # Find task with id requested
    task = Task.objects.filter(pk=task_id, active=True,
                               projectDepartment_id__projectdepartmentemployeerole__employee_id=employee,
                               production_goal__isnull=False).distinct().first()
    if task is None:
        return HttpResponseBadRequest("The task could not be found")

    # Get all dates between start and end
    dates = []
    str_dates = []
    d1 = datetime.strptime(start_date[0:19]+start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19]+end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1         # timedelta

    for i in range(delta.days + 1):
        str_dates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))
    print(len(dates))

    data = {'dates': str_dates, 'task': {'task_id': task.id, 'name': task.name,
                                         'real_productivity': [], 'expected_productivity': []}}

    # Save productivity for each  date
    # for each date, we will find the asociated timelog
    for log_date in dates:
        log = TimeLog.objects.filter(task_id=task.id, workDate__year=log_date.year, workDate__month=log_date.month,
                                     workDate__day=log_date.day, employee_id=employee).first()
        if log is None:
            # He did not work that day
            total_productivity = 0
        else:
            total_produced_units = log.produced_units
            total_duration = log.duration
            if total_duration == 0:
                total_productivity = 0
            else:
                # Duration is in minutes, so we multiply by 60 (duration is in the denominator)
                total_productivity = 60*total_produced_units/total_duration

        # Find the registry date of production goal evolution which is closest to the date
        expected_productivity = GoalEvolution.objects.filter(task_id_id=task.id,
                                                             registryDate__gte=log_date).first()

        # If we do not find the goal or if the date is after the last task update, it may be the current task goal
        if expected_productivity is None or task.registryDate <= log_date:
            expected_productivity = task.production_goal
        else:
            expected_productivity = expected_productivity.production_goal

        data["task"]["real_productivity"].append(total_productivity)
        data["task"]["expected_productivity"].append(expected_productivity)

    return JsonResponse(data)

@login_required
def ajax_profit_per_date(request, employee_id):
    """
    # url = employee/ajax_profit_per_date/<employee_id>
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
    #/employee/ajaxAcumProfit/1/

    #devuelve lo siguiente
    #{"acumExpenses": [0, 1457.18015695298, 3071.32603956358, 4438.9463044226895, 6465.819587171869, 7912.658013249849, 9791.46399488711, 11615.32872003681, 13494.726436052111, 15102.72092592163, 16718.442225021892, 18327.93613617256, 20841.87940297534, 22953.949544558982, 24314.625169466122, 25683.231076691303, 27287.16055422502, 28760.84364198999, 31104.25163724206, 32808.89759982555, 34747.27999087272, 36150.9847742294, 37523.6098087571, 38600.05927001698, 40953.76583717958, 42469.88703139726, 44081.49130458021, 45420.3135021882, 47945.57927018715, 49368.262834629466, 51133.932803674485],
    "acumIncome": [0, 155861.848663544, 262457.90948135697, 396454.85575838294, 572637.4741922909, 703418.0032829699, 889130.2419483919, 1057821.248373874, 1259349.275922576, 1393310.956579081, 1539441.608896949, 1700420.3827038072, 1955067.034572835, 2187486.6539142523, 2300530.309442004, 2429378.038836404, 2615789.2939997134, 2742614.2371285204, 3004214.3219032744, 3205025.4834073624, 3363963.7766520614, 3552325.908039063, 3718850.184141958, 3833661.86021891, 4044009.6991582112, 4159278.365569177, 4285423.634163346, 4417334.086840815, 4692230.750316469, 4819759.243153938, 4997733.5628708275],
    "dates": ["2017-03-21", "2017-03-22", "2017-03-23", "2017-03-24", "2017-03-25", "2017-03-26", "2017-03-27", "2017-03-28", "2017-03-29", "2017-03-30", "2017-03-31", "2017-04-01", "2017-04-02", "2017-04-03", "2017-04-04", "2017-04-05", "2017-04-06", "2017-04-07", "2017-04-08", "2017-04-09", "2017-04-10", "2017-04-11", "2017-04-12", "2017-04-13", "2017-04-14", "2017-04-15", "2017-04-16", "2017-04-17", "2017-04-18", "2017-04-19", "2017-04-20"],
    "income": [0, 155861.848663544, 106596.060817813, 133996.946277026, 176182.618433908, 130780.529090679, 185712.238665422, 168691.006425482, 201528.027548702, 133961.680656505, 146130.652317868, 160978.773806858, 254646.651869028, 232419.619341417, 113043.655527752, 128847.7293944, 186411.255163309, 126824.943128807, 261600.084774754, 200811.161504088, 158938.293244699, 188362.131387002, 166524.276102895, 114811.676076952, 210347.838939301, 115268.666410966, 126145.268594169, 131910.452677469, 274896.663475654, 127528.492837469, 177974.319716889],
    "expenses": [0, 1457.18015695298, 1614.1458826106, 1367.62026485911, 2026.87328274918, 1446.83842607798, 1878.80598163726, 1823.8647251497, 1879.3977160153, 1607.99448986952, 1615.72129910026, 1609.49391115067, 2513.94326680278, 2112.07014158364, 1360.67562490714, 1368.60590722518, 1603.92947753372, 1473.68308776497, 2343.40799525207, 1704.64596258349, 1938.38239104717, 1403.70478335668, 1372.6250345277, 1076.44946125988, 2353.7065671626, 1516.12119421768, 1611.60427318295, 1338.82219760799, 2525.26576799895, 1422.68356444232, 1765.66996904502]}  "expected_productivity": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 4.0, 4.0, 2.0, 2.0, 2.0]}}
    """

    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today() - timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
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

    check_metrics_authorized_for_employee(request.user, employee_id)
    # Get all dates between start and end
    dates = []
    str_dates = []

    d1 = datetime.strptime(start_date[0:19] + start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19] + end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1  # timedelta
    for i in range(delta.days + 1):
        str_dates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))

    data = {'dates': str_dates, 'expenses': [], 'income': [], 'acumExpenses': [], 'acumIncome': []}

    # Profit
    # for each date, we will find all logs, calculate the sum and acumulate it
    index = 0
    for log_date in dates:
        logs = TimeLog.objects.filter(employee_id=employee_id,
                                      workDate__year=log_date.year, workDate__month=log_date.month,
                                      workDate__day=log_date.day).distinct()
        expenses = logs.aggregate(
            total_expenses=Sum(F("duration") / 60.0 * F("employee_id__price_per_hour"), output_field=FloatField()))[
            "total_expenses"]
        expenses = expenses if expenses is not None else 0
        income = logs.aggregate(total_income=Sum(F("task_id__price_per_unit") * F("produced_units"))
                                )["total_income"]
        income = income if income is not None else 0

        data['expenses'].append(expenses)
        data['income'].append(income)
        if index == 0:
            data['acumExpenses'].append(expenses)
            data['acumIncome'].append(income)
        else:
            data['acumExpenses'].append(data['acumExpenses'][index - 1] + expenses)
            data['acumIncome'].append(data['acumIncome'][index - 1] + income)
        index += 1
    return JsonResponse(data)


def ajax_profit_per_date_in_project(request, employee_id, project_id):
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

    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today() - timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
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

    check_metrics_authorized_for_employee_in_project(request.user, employee_id, project_id)
    # Get all dates between start and end
    dates = []
    str_dates = []

    d1 = datetime.strptime(start_date[0:19] + start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19] + end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1  # timedelta
    for i in range(delta.days + 1):
        str_dates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))

    data = {'dates': str_dates, 'expenses': [], 'income': [], 'acumExpenses': [], 'acumIncome': []}

    # Profit
    # for each date, we will find all logs, calculate the sum and acumulate it
    index = 0
    for log_date in dates:
        logs = TimeLog.objects.filter(employee_id=employee_id,
                                      employee_id__projectdepartmentemployeerole__projectDepartment_id__project_id=project_id,
                                      workDate__year=log_date.year, workDate__month=log_date.month,
                                      workDate__day=log_date.day).distinct()
        expenses = logs.aggregate(
            total_expenses=Sum(F("duration") / 60.0 * F("employee_id__price_per_hour"), output_field=FloatField()))[
            "total_expenses"]
        expenses = expenses if expenses is not None else 0
        income = logs.aggregate(total_income=Sum(F("task_id__price_per_unit") * F("produced_units"))
                                )["total_income"]
        income = income if income is not None else 0

        data['expenses'].append(expenses)
        data['income'].append(income)
        if index == 0:
            data['acumExpenses'].append(expenses)
            data['acumIncome'].append(income)
        else:
            data['acumExpenses'].append(data['acumExpenses'][index - 1] + expenses)
            data['acumIncome'].append(data['acumIncome'][index - 1] + income)
        index += 1
    return JsonResponse(data)


def ajax_get_employee_projects(employee_id):
    projects = Project.objects.filter(projectdepartment__projectdepartmentemployeerole__employee_id=employee_id,
                                      deleted=False)
    data = serializers.serialize('json', projects, fields=('id', 'name',))
    return HttpResponse(data)


########################################################################################################################
########################################################################################################################
########################################################################################################################

def check_metrics_authorized_for_employee(user, employee_id):
    """Raises 403 if the current actor is not allowed to obtain metrics for the department"""
    if not user.is_authenticated():
        raise PermissionDenied

    employee = get_object_or_404(Employee, id=employee_id)
    logged = user.actor

    # Check that the companies match
    if logged.company_id != employee.company_id:
        raise PermissionDenied


def check_metrics_authorized_for_employee_in_project(user, employee_id, project_id):
    """
    Raises 403 if the current actor is not allowed to obtain metrics for the department

    Optional at the end:
    if logged.user_type == 'E'
        If it's not an admin, check that it has role EXECUTIVE (50) or higher for any project in the department
        try
            ProjectDepartmentEmployeeRole.objects.get(employee_id=logged, role_id__tier__gte=50, projectDepartment_id__project_id=project)
        except ObjectDoesNotExist:
            raise PermissionDenied
    """
    if not user.is_authenticated():
        raise PermissionDenied

    employee = get_object_or_404(Employee, id=employee_id)
    project = get_object_or_404(Project, id=project_id)
    logged = user.actor

    # Check that the companies match
    if logged.company_id != employee.company_id:
        raise PermissionDenied

    if logged.company_id != project.company_id:
        raise PermissionDenied

    if employee.company_id != project.company_id:
        raise PermissionDenied


def create_employee_user(form):
    """Creates an employee user supposing the data in the form is OK"""
    username = form.cleaned_data['username']
    password = form.cleaned_data['password1']
    email = form.cleaned_data['email']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']

    return User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)


def create_employee(employee_user, admin, form):
    """Creates an employee supposing the data in the form is OK"""
    user = employee_user
    user_type = 'E'
    identifier = form.cleaned_data['identifier']
    phone = form.cleaned_data['phone']
    company = admin.company_id
    picture = form.cleaned_data['photo']
    price_per_hour = form.cleaned_data['price_per_hour']
    return Employee.objects.create(user=user, user_type=user_type, identifier=identifier, phone=phone, company_id=company, picture=picture,price_per_hour=price_per_hour)


def check_passwords(form):
    """Checks the password is equal in the password repeat form field"""
    return form.cleaned_data['password1'] == form.cleaned_data['password2']


def notify_password_change(email, name):
    """Notifies a password change to someone by sending them an email"""
    send_mail(ugettext_lazy("register_changepw_subject"),
              "employee/employee_changepw_email.html", [email], "employee/employee_changepw_email.html",
              {'html': True, 'employee_name': name})


def send_register_email(email, name):
    """Emails someone who has been registered from a company"""
    send_mail(ugettext_lazy("register_mail_subject"),
              "employee/employee_register_email.html", [email], "employee/employee_register_email.html",
              {'html': True, 'employee_name': name})
