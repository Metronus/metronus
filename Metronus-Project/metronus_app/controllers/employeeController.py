from django.contrib.auth.models                  import User
from django.shortcuts                            import render
from django.shortcuts                            import render_to_response, get_object_or_404
from django.core.urlresolvers                    import reverse
from django.http                                 import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.template.context                     import RequestContext
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from django.utils.translation                    import ugettext_lazy
from django.db.models                            import Sum,Max


from metronus_app.forms.employeeRegisterForm     import EmployeeRegisterForm
from metronus_app.forms.employeeEditForm         import EmployeeEditForm
from metronus_app.forms.employeePasswordForm     import EmployeePasswordForm
from metronus_app.model.employee                 import Employee
from metronus_app.model.employeeLog              import EmployeeLog
from metronus_app.model.administrator            import Administrator
from metronus_app.model.task                     import Task
from metronus_app.model.goalEvolution            import GoalEvolution
from metronus_app.model.timeLog                  import TimeLog
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

from metronus_app.common_utils                   import (get_current_admin_or_403, checkImage, get_current_employee_or_403, send_mail
                                                        , is_email_unique, is_username_unique)
from datetime                                           import date, timedelta,datetime

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
            if not checkPasswords(form):
                errors.append('employeeCreation_passwordsDontMatch')

            # Check that the username is unique
            if not is_username_unique(form.cleaned_data["username"]):
                errors.append('employeeCreation_usernameNotUnique')

            # Check that the email is unique
            if not is_email_unique(form.cleaned_data["email"]):
                errors.append('employeeCreation_emailNotUnique')

            # Check that the image is OK
            if not checkImage(form, 'photo'):
                errors.append('employeeCreation_imageNotValid')

            # Check that the price is OK
            if form.cleaned_data['price_per_hour']<=0:
                errors.append('employeeCreation_priceNotValid')

            if not errors:
                # Everything is OK, create the employee
                employee_user = createEmployeeUser(form)
                employee = createEmployee(employee_user, admin, form)
                EmployeeLog.objects.create(employee_id=employee, event="A", price_per_hour=employee.price_per_hour)
                send_register_email(form.cleaned_data["email"], form.cleaned_data["first_name"])

                if "redirect" in request.GET: # Redirect to the created employee
                    return HttpResponseRedirect('/employee/view/' + form.cleaned_data["username"] + '/')
                else: # Return a new form
                    return render(request, 'employee/employee_register.html', {'form': EmployeeRegisterForm(), 'success': True})
            else:
                # There are errors
                return render(request, 'employee/employee_register.html', {'form': form, 'errors': errors})

        # Form is not valid
        else:
            return render(request, 'employee/employee_register.html', {'form': form, 'errors': ['employeeCreation_formNotValid']})
    else:
        # Another request method
        raise PermissionDenied

    

def list(request):
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
    producti

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
        form = EmployeeEditForm(initial = {
            'first_name': employee.user.first_name,
            'last_name': employee.user.last_name,
            'email': employee.user.email,
            'identifier': employee.identifier,
            'phone': employee.phone,
            'price_per_hour':employee.price_per_hour
        })

        return render(request, 'employee/employee_edit.html', {'form': form})

    elif request.method == "POST":
        # Process the received form
        
        form = EmployeeEditForm(request.POST)
        if form.is_valid():
            errors = []
            # Check that the price is OK
            if form.cleaned_data['price_per_hour']<=0:
                errors.append('employeeCreation_priceNotValid')
            if not errors:
                # Update employee data
                employee.identifier = form.cleaned_data["identifier"]
                employee.phone = form.cleaned_data["phone"]
                #New log if the salary has changed
                newLog=employee.price_per_hour != form.cleaned_data["price_per_hour"];
                    
                employee.price_per_hour = form.cleaned_data["price_per_hour"]

                # Update user data
                user = employee.user
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.email = form.cleaned_data["email"]

                user.save()
                employee.save()
                
                #New log if the salary has changed
                if newLog:
                    EmployeeLog.objects.create(employee_id=employee, event="C", price_per_hour=form.cleaned_data["price_per_hour"])
                return HttpResponseRedirect('/employee/view/' + username + '/')
            else:
                # There are errors
                return render(request, 'employee/employee_edit.html', {'form': form, 'errors': errors})

        else:
            # Form is not valid
            return render(request, 'employee/employee_edit.html', {'form': form, 'errors': ['employeeCreation_formNotValid']})

    else:
        raise PermissionDenied

def updatePassword(request, username):
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
    return HttpResponseRedirect('/employee/list/')

###AJAX methods
def ajax_productivity_per_task(request,username):
    # url = employee/ajax_productivity_per_task/<username>
    # Devuelve un objeto cuyas claves son las ID de los proyectos y sus valores un objeto 
    #{'name': ..., 'total_productivity': X,'expected_productivity':Y} (X e Y en unidades goal_description/hora)
    
    #Ejemplo:
    #/employee/ajax_productivity_per_task/JoseGavilan
    
    #devuelve lo siguiente
    #{"3": {"total_productivity": 0.7125, "expected_productivity": 2.0, "name": "Hacer cosas de front"}}
    
    # Check that the user is logged in and it's an administrator or with permissions
    try:
        logged = get_current_admin_or_403(request)
    except PermissionDenied:
        logged = get_current_employee_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check the company is the same for logged and the searched employee
    if employee.company_id != logged.company_id:
        raise PermissionDenied

    #Find tasks with timelog in date range and annotate the sum of the production and time
    tasks = Task.objects.filter(active=True,projectDepartment_id__projectdepartmentemployeerole__employee_id=employee,
            production_goal__isnull=False).distinct().annotate(
            total_produced_units=Sum("timelog__produced_units"),total_duration=Sum("timelog__duration"))

    data = {}
    #Save productivity for each task
    for task in tasks:
        
        total_produced_units= task.total_produced_units
        total_duration= task.total_duration
        if total_duration is None or total_produced_units is None or total_duration==0: 
            total_productivity = 0
        else:
            #duration is in minutes,so we multiply by 60 (duration is in the denominator)
            total_productivity = 60*total_produced_units/total_duration

        data[task.id] = {
                            'name': task.name,
                            'expected_productivity':task.production_goal,
                            'total_productivity': total_productivity
                        }

    return JsonResponse(data)

def ajax_productivity_per_task_and_date(request,username):
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
    
    # Get and parse the dates
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

    # Check that the user is logged in and it's an administrator or with permissions
    try:
        logged = get_current_admin_or_403(request)
    except PermissionDenied:
        logged = get_current_employee_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check the company is the same for logged and the searched employee
    if employee.company_id != logged.company_id:
        raise PermissionDenied

    task_id=request.GET.get("task_id")
    #Find task with id requested
    task = Task.objects.filter(pk=task_id,active=True,projectDepartment_id__projectdepartmentemployeerole__employee_id=employee,production_goal__isnull=False).distinct().first()
    if task is None:
        return HttpResponseBadRequest("The task could not be found")

    #Get all dates between start and end
    dates=[]
    strDates=[]
    d1 = datetime.strptime(start_date[0:19]+start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19]+end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1         # timedelta

    for i in range(delta.days + 1):
        strDates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))
    print (len(dates))

    data = {'dates':strDates,'task':{'task_id':task.id,'name': task.name,'real_productivity':[],'expected_productivity':[]}}
    

    #Save productivity for each  date
    #for each date, we will find the asociated timelog
    for logDate in dates:
        log=TimeLog.objects.filter(task_id=task.id,workDate__year=logDate.year,workDate__month=logDate.month
            ,workDate__day=logDate.day,employee_id=employee).first()
        
        if log is None:
            #he did not work that day
            total_productivity=0
        else:
            total_produced_units= log.produced_units
            total_duration= log.duration
            if  total_duration==0: 
                total_productivity = 0
            else:
                #duration is in minutes, so we multiply by 60 (duration is in the denominator)
                total_productivity = 60*total_produced_units/total_duration
        
        #find the registry date of production goal evolution which is closest to the date
        expected_productivity=GoalEvolution.objects.filter(task_id_id=task.id,
            registryDate__gte=logDate).first()

        #if we do not find the goal or if the date is after the last task update, it may be the current task goal
        if expected_productivity is None or task.registryDate<=logDate:
            expected_productivity=task.production_goal
        else:
            expected_productivity=expected_productivity.production_goal

        data["task"]["real_productivity"].append(total_productivity)
        data["task"]["expected_productivity"].append(expected_productivity)

    return JsonResponse(data)


########################################################################################################################################
########################################################################################################################################
########################################################################################################################################

def createEmployeeUser(form):
    username = form.cleaned_data['username']
    password = form.cleaned_data['password1']
    email = form.cleaned_data['email']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']

    return User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

def createEmployee(employeeUser, admin, form):
    user = employeeUser
    user_type = 'E'
    identifier = form.cleaned_data['identifier']
    phone = form.cleaned_data['phone']
    company = admin.company_id
    picture = form.cleaned_data['photo']
    price_per_hour=form.cleaned_data['price_per_hour']
    return Employee.objects.create(user=user, user_type=user_type, identifier=identifier, phone=phone, company_id=company, picture=picture,price_per_hour=price_per_hour)

def checkPasswords(form):
    return form.cleaned_data['password1'] == form.cleaned_data['password2']

def notify_password_change(email, name):
    send_mail(ugettext_lazy("register_changepw_subject"), "employee/employee_changepw_email.html", [email], "employee/employee_changepw_email.html",
              {'html': True, 'employee_name': name})

def send_register_email(email, name):
    send_mail(ugettext_lazy("register_mail_subject"), "employee/employee_register_email.html", [email], "employee/employee_register_email.html",
              {'html': True, 'employee_name': name})
