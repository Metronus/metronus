from django.contrib.auth.models                  import User
from django.shortcuts                            import render
from django.shortcuts                            import render_to_response, get_object_or_404
from django.core.urlresolvers                    import reverse
from django.http                                 import HttpResponseRedirect, JsonResponse
from django.template.context                     import RequestContext
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied

from metronus_app.forms.employeeRegisterForm     import EmployeeRegisterForm
from metronus_app.forms.employeeEditForm         import EmployeeEditForm
from metronus_app.forms.employeePasswordForm     import EmployeePasswordForm
from metronus_app.model.employee                 import Employee
from metronus_app.model.employeeLog              import EmployeeLog
from metronus_app.model.administrator            import Administrator
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

from metronus_app.common_utils                   import get_current_admin_or_403, checkImage, get_current_employee_or_403

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
    
    template:
        employee_register.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    # If it's a GET request, return an empty form
    if request.method == "GET":
        return render(request, 'employee_register.html', {'form': EmployeeRegisterForm()})

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

            # Check that the image is OK
            if not checkImage(form, 'photo'):
                errors.append('employeeCreation_imageNotValid')

            if not errors:
                # Everything is OK, create the employee
                employeeUser = createEmployeeUser(form)
                employee = createEmployee(employeeUser, admin, form)
                EmployeeLog.objects.create(employee_id=employee, event="A")

                if "redirect" in request.GET: # Redirect to the created employee
                    return HttpResponseRedirect('/employee/view/' + form.cleaned_data["username"] + '/')
                else: # Return a new form
                    return render(request, 'employee_register.html', {'form': EmployeeRegisterForm(), 'success': True})
            else:
                # There are errors
                return render(request, 'employee_register.html', {'form': form, 'errors': errors})

        # Form is not valid
        else:
            return render(request, 'employee_register.html', {'form': form, 'errors': ['employeeCreation_formNotValid']})
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
    return render(request, 'employee_list.html', {'employees': employees})

def view(request, username):
    """
    url = employee/view/<username>

    parameters/returns:
    employee: datos del empleado
    employee_roles: objetos ProjectDepartmentEmployeeRole (bibah) con todos los roles del empleado

    template: employee_view.html
    """

    # Check that the user is logged in and it's an administrator

    currentEmployee = get_current_employee_or_403(request)
    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check that the admin has permission to view that employee
    if employee.company_id != currentEmployee.company_id:
        raise PermissionDenied

    employee_roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee)

    return render(request, 'employee_view.html', {'employee': employee, 'employee_roles': employee_roles})

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
            'phone': employee.phone
        })

        return render(request, 'employee_edit.html', {'form': form})

    elif request.method == "POST":
        # Process the received form
        
        form = EmployeeEditForm(request.POST)
        if form.is_valid():
            
            # Update employee data
            employee.identifier = form.cleaned_data["identifier"]
            employee.phone = form.cleaned_data["phone"]

            # Update user data
            user = employee.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]

            user.save()
            employee.save()

            return HttpResponseRedirect('/employee/view/' + username + '/')

        else:
            # Form is not valid
            return render(request, 'employee_edit.html', {'form': form, 'errors': ['employeeCreation_formNotValid']})

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

    EmployeeLog.objects.create(employee_id=employee, event="B")
    return HttpResponseRedirect('/employee/list/')


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

    return Employee.objects.create(user=user, user_type=user_type, identifier=identifier, phone=phone, company_id=company, picture=picture)

def checkPasswords(form):
    return form.cleaned_data['password1'] == form.cleaned_data['password2']

def notify_password_change(email):
    pass # TODO

def is_username_unique(username):
    return User.objects.filter(username=username).count() == 0