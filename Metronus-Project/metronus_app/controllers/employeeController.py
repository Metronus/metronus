from django.contrib.auth.models         import User
from django.shortcuts                   import render_to_response
from django.core.urlresolvers           import reverse
from django.http                        import HttpResponseRedirect
from django.template.context            import RequestContext
from django.core.exceptions             import ObjectDoesNotExist
from django.http                        import HttpResponseForbidden

from metronus_app.forms.employeeRegisterForm     import EmployeeRegisterForm
from metronus_app.model.employee                 import Employee
from metronus_app.model.administrator            import Administrator

def create(request):
    """
    parameters/returns:
    form: formulario con los datos necesarios para el registro del empleado
    success: opcional, si se ha tenido éxito al crear un empleado
    
    template:
    employee_register.html
    """

    # Check that the user is logged in
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    # Check that the current user is an administrator
    admin = get_current_admin(request)

    if admin == None:
        return HttpResponseForbidden()

    # If it's a GET request, return an empty form
    if request.method == "GET":
        form = EmployeeRegisterForm()
    elif request.method == "POST":
    # We are serving a POST request
        form = EmployeeRegisterForm(request.POST)

        if form.is_valid() and checkPasswords(form):
            employeeUser = createEmployeeUser(form)
            employee = createEmployee(employeeUser, admin, form)
            return render_to_response('employee_register.html', {'form': EmployeeRegisterForm(), 'success': True})
    else:
        return HttpResponseForbidden()

    return render_to_response('employee_register.html', {'form': form, }, context_instance=RequestContext(request))


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

def get_current_admin(request):
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return None

def checkPasswords(form):
    return form.cleaned_data['password1'] == form.cleaned_data['password2']