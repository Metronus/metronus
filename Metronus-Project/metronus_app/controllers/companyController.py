from metronus_app.forms.registrationForm import RegistrationForm
from metronus_app.forms.companyForm import CompanyForm
from metronus_app.model.company import Company
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import JsonResponse

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from metronus_app.common_utils import get_current_admin_or_403
from django.core.exceptions import PermissionDenied


def create(request):
    """
    parameters/returns:
    form: el formulario con los datos de la compañía y el administrador de la compañía

    template:
    company_form.html
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegistrationForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid() and checkPasswords(form):
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            company = createCompany(form)
            registerAdministrator(form, company)
            return HttpResponseRedirect(reverse('login'))

    # if a GET (or any other method) we'll create a blank form
    else:
        # form = DepartmentForm(initial={"department_id":0})
        form = RegistrationForm()
    return render_to_response('company_register.html', {'form': form})


def edit(request, cif):
    """
    url = company/edit/<cif>

    parameters/returns:
    form: formulario de edicion de datos de la compañía

    template: company_edit.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    company = get_object_or_404(Company, cif=cif)

    # Check that the admin has permission to view that company
    if company.pk != admin.company_id:
        raise PermissionDenied

    if request.method == "GET":
        # Return a form filled with the employee's data
        form = CompanyForm(initial={
            'company_email': company.company_email,
            'company_phone': company.phone,
            'logo': company.logo,
        })
    elif request.method == "POST":
        # Process the received form

        form = CompanyForm(request.POST)
        if form.is_valid():
            # Company data
            company.company_email = form.cleaned_data["company_email"]
            company.company_phone = form.cleaned_data["company_phone"]
            company.logo = form.cleaned_data["logo"]
            company.save()

            return HttpResponseRedirect('/company/edit/' + cif + '/')

    else:
        raise PermissionDenied

    return render_to_response('company_edit.html', {'form': form})

def delete(request, cif):
    """
    url = company/delete/<cif>

    parameters/returns:
    Nada, redirecciona al inicio

    template: ninguna
    """
    pass  # TODO

#Auxiliar methods, containing the operation logic

def createCompany(form):
    cif=form.cleaned_data['cif']
    company_name = form.cleaned_data['company_name']
    short_name = form.cleaned_data['short_name']
    email = form.cleaned_data['company_email']
    phone = form.cleaned_data['company_phone']
    logo = form.cleaned_data['logo']

    company = Company.objects.create(cif=cif, company_name=company_name, short_name=short_name, email=email, phone=phone, logo=logo)
    return company


def registerAdministrator(form, company):
    username = form.cleaned_data['username']
    password = form.cleaned_data['password1']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    user_email = form.cleaned_data['user_email']

    admin = User.objects.create_user(username=username, password=password, email=user_email, first_name=first_name, last_name=last_name)

    identifier = form.cleaned_data['identifier']
    phone = form.cleaned_data['phone']

    Administrator.objects.create(user=admin, user_type="A", identifier=identifier, phone=phone, company_id=company)


def checkPasswords(form):
    """
    checks if two passwords are the same
    """
    return form.cleaned_data['password1'] == form.cleaned_data['password2']

def validateCIF(request):
    cif = request.GET.get('cif', None)
    data = {
        'is_taken': 1 == 1
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)