from django.contrib.auth.models                  import User
from django.shortcuts                            import render_to_response, get_object_or_404
from django.core.urlresolvers                    import reverse
from django.http                                 import HttpResponseRedirect
from django.template.context                     import RequestContext
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied

from metronus_app.forms.employeeRegisterForm     import EmployeeRegisterForm
from metronus_app.forms.employeeEditForm         import EmployeeEditForm
from metronus_app.model.employee                 import Employee
from metronus_app.model.employeeLog              import EmployeeLog
from metronus_app.model.administrator            import Administrator
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

from metronus_app.common_utils                   import get_current_admin_or_403

def create(request):
    """
    parameters/returns:
    form: formulario con los datos necesarios para el registro del empleado
    success: opcional, si se ha tenido éxito al crear un empleado
    
    template:
    employee_register.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    # If it's a GET request, return an empty form
    if request.method == "GET":
        form = EmployeeRegisterForm()
    elif request.method == "POST":
    # We are serving a POST request
        form = EmployeeRegisterForm(request.POST)

        if form.is_valid() and checkPasswords(form):
            employeeUser = createEmployeeUser(form)
            employee = createEmployee(employeeUser, admin, form)
            EmployeeLog.objects.create(employee_id=employee, event="A")
            return render_to_response('employee_register.html', {'form': EmployeeRegisterForm(), 'success': True})
    else:
        raise PermissionDenied

    return render_to_response('employee_register.html', {'form': form})

def list(request):
    """
    parameters/returns:
    employees: lista de objetos employee a los que tiene acceso el administrador (los que están en su empresa)

    template: employee_list.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    employees = Employee.objects.filter(company_id=admin.company_id, user__is_active=True)
    return render_to_response('employee_list.html', {'employees': employees})

def view(request, username):
    """
    url = employee/view/<username>

    parameters/returns:
    employee: datos del empleado
    employee_roles: objetos ProjectDepartmentEmployeeRole (bibah) con todos los roles del empleado

    template: employee_view.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    employee = get_object_or_404(Employee, user__username=username, user__is_active=True)

    # Check that the admin has permission to view that employee
    if employee.company_id != admin.company_id:
        raise PermissionDenied

    employee_roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee)

    return render_to_response('employee_view.html', {'employee': employee, 'employee_roles': employee_roles})

def edit(request, username):
    """
    url = employee/edit/<username>

    parameters/returns:
    form: formulario de edicion de datos de empleado

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
    elif request.method == "POST":
        # Process the received form
        
        form = EmployeeEditForm(request.POST)
        if form.is_valid() and checkPasswords(form):
            
            # Update employee data
            employee.identifier = form.cleaned_data["identifier"]
            employee.phone = form.cleaned_data["phone"]

            # Update user data
            user = employee.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]

            # If a new password has been specified, change the current one and notify the user
            if form.cleaned_data["password1"]:
                user.set_password(form.cleaned_data["password1"])
                notify_password_change(user.email)

            user.save()
            employee.save()

            return HttpResponseRedirect('/employee/view/' + username + '/')

    else:
        raise PermissionDenied

    return render_to_response('employee_edit.html', {'form': form})

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

    return Employee.objects.create(user=user, user_type=user_type, identifier=identifier, phone=phone, company_id=company)

def checkPasswords(form):
    return form.cleaned_data['password1'] == form.cleaned_data['password2']

def notify_password_change(email):
    pass # TODO