from metronus_app.forms.registrationForm import RegistrationForm
from metronus_app.forms.companyForm import CompanyForm
from metronus_app.model.company import Company
from metronus_app.model.companyLog import CompanyLog
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from metronus_app.common_utils import get_current_admin_or_403, get_or_none
from django.core.exceptions import PermissionDenied

from PIL import Image
from django.core.mail import send_mail


# Image limit parameters
FILE_SIZE = 100000000
HEIGHT = 256
WIDTH = 256
VALID_FORMATS = ['JPEG', 'JPG', 'PNG']


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
        if form.is_valid() and checkPasswords(form) and checkImage(form):
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            company = createCompany(form)
            administrator = registerAdministrator(form, company)

            # This sends an information email to the company and to the admin

            #send_mail('Metronus Info.', 'Registrado :)', 'info@metronus.es',
            #          [company.email, administrator.user.email], fail_silently=False,)

            return HttpResponseRedirect('/' + company.short_name + '/login/')

    # if a GET (or any other method) we'll create a blank form
    else:
        # form = DepartmentForm(initial={"department_id":0})
        form = RegistrationForm()
    return render(request, 'company_register.html', {'form': form})


@login_required
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


@login_required
def view(request, cif):
    """
    url = company/view/<cif>

    parameters/returns:
    company: datos de la compañía

    template: company_view.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    company = get_object_or_404(Company, cif=cif)

    # Check that the admin has permission to view that company
    if company.pk != admin.company_id:
        raise PermissionDenied

    return render(request, 'company_view.html', {'company': company})


@login_required
def delete(request):
    """
    url = company/delete

    parameters/returns:
    Nada, redirecciona al inicio

    template: ninguna
    """
    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    company = get_object_or_404(Company, pk=admin.company_id)

    # Check that the admin has permission to view that company
    if company.pk != admin.company_id:
        raise PermissionDenied

    CompanyLog.objects.create(cif=company.cif, company_name=company.company_name, registryDate=company.registryDate)

    company.delete()

    return HttpResponseRedirect('')


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
    password = form.cleaned_data['password']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    user_email = form.cleaned_data['admin_email']

    admin = User.objects.create_user(username=username, password=password, email=user_email, first_name=first_name, last_name=last_name)

    identifier = form.cleaned_data['admin_identifier']
    phone = form.cleaned_data['admin_phone']

    administrator = Administrator.objects.create(user=admin, user_type="A", identifier=identifier, phone=phone, company_id=company)

    return administrator

def checkPasswords(form):
    """
    checks if two passwords are the same
    """
    return form.cleaned_data['password'] == form.cleaned_data['repeatPassword']


def checkImage(form):
    """
    checks if logo has the correct dimensions
    """
    ret = False

    logo = form.cleaned_data['logo']
    if logo is not None:
        image = Image.open(logo, mode="r")
        xsize, ysize = image.size

        print(logo)
        for i in VALID_FORMATS:
            if i == image.format:
                ret = True

        return xsize <= WIDTH and ysize <= HEIGHT and ret
    else:
        return True


def validateCIF(request):
    """
    checks if the company cif already exist
    """
    cif = request.GET.get('cif', None)

    check = get_or_none(Company, cif=cif)
    if check is not None:
        check = check.cif

    data = {
        'is_taken': cif == check
    }
    if data['is_taken']:
        data['error_message'] = 'ERROR'
    return JsonResponse(data)


def validateAdmin(request):
    """
    checks if the company administrator is registered
    """
    admin = request.GET.get('admin', None)

    check = get_or_none(Administrator, user__username=admin)
    if check is not None:
        check = check.user.username

    data = {
        'is_taken': admin == check
    }
    if data['is_taken']:
        data['error_message'] = 'ERROR'
    return JsonResponse(data)