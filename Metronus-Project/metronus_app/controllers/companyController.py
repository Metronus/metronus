from metronus_app.forms.registrationForm import RegistrationForm
from metronus_app.forms.companyForm import CompanyForm
from metronus_app.model.company import Company
from metronus_app.model.companyLog import CompanyLog
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from metronus_app.common_utils import (get_current_admin_or_403, check_image, send_mail, is_email_unique,
                                       get_or_none, is_username_unique, is_cif_unique, is_company_email_unique)
from django.core.exceptions import PermissionDenied


def create(request,
           email_template_name='company/company_register_email.html',
           html_email_template_name='company/company_register_email.html'):
    """
    parameters/returns:
    form: el formulario con los datos de la compañía y el administrador de la compañía

    template:
    company_form.html
    """
    # If it's a GET request, return an empty form
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegistrationForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            errors = []

            # Check that the passwords match
            if not check_passwords(form):
                errors.append('passwordsDontMatch')

            # Check that the username is unique
            if not is_username_unique(form.cleaned_data["username"]):
                errors.append('companyRegister_usernameNotUnique')

            # Check that the admin email is unique
            if Company.objects.filter(email=form.cleaned_data["company_email"]).exists():
                errors.append('companyRegister_companyEmailNotUnique')

            # Check that the admin email is unique
            if not is_email_unique(form.cleaned_data["admin_email"]):
                errors.append('companyRegister_adminEmailNotUnique')

            # Check that the CIF is unique
            if not is_cif_unique(form.cleaned_data["cif"]):
                errors.append('companyRegister_cifNotUnique')

            # Check that the image is OK
            if not check_image(form, 'logo'):
                errors.append('company_imageNotValid')

            if not form.cleaned_data["terms_agree"]:
                errors.append("agree_terms_error")

            if not errors:
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                company = create_company(form)
                administrator = register_administrator(form, company)

                # This sends an information email to the company and to the admin

                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain

                use_https = True
                context = {
                    'domain': domain,
                    'site_name': site_name,
                    'admin': administrator,
                    'company': company.short_name,
                    'protocol': 'https' if use_https else 'http',
                    'html': True
                }

                send_mail('Metronus Info.', email_template_name,
                          [company.email, administrator.user.email], html_email_template_name, context)

                # Login the administrator and send him to the dashboard
                logged_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                login(request, logged_user)
                return HttpResponseRedirect("/dashboard/view")
            else:
                return render(request, 'company/company_register.html', {'form': form, 'errors': errors})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegistrationForm()
    return render(request, 'company/company_register.html', {'form': form})


@login_required
def edit(request):
    """
    Se escoge la comoañía correspondiente al administrador que la edita

    url = company/edit

    parameters/returns:
    form: formulario de edicion de datos de la compañía

    template: company_edit.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    company = get_object_or_404(Company, cif=admin.company_id.cif)

    if request.method == "GET":
        # Return a form filled with the employee's data
        form = CompanyForm(initial={
            'visible_short_name': company.visible_short_name,
            'company_email': company.email,
            'company_phone': company.phone,
        })
    elif request.method == "POST":
        # Process the received form

        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            errors = []

            # Check that the image is OK
            if not check_image(form, 'logo'):
                errors.append('company_imageNotValid')
            # Check that the company email is unique
            if Company.objects.filter(email=form.cleaned_data["company_email"]).exists() and company.email!=form.cleaned_data["company_email"]:
                errors.append('companyRegister_companyEmailNotUnique')

            if not errors:
                # Company data
                company.visible_short_name = form.cleaned_data["visible_short_name"]
                company.email = form.cleaned_data["company_email"]
                company.phone = form.cleaned_data["company_phone"]

                if form.cleaned_data["logo"]:
                    # Don't overwrite the current logo with an empty one
                    # if the administrator hasn't uploaded one in the form
                    company.logo = form.cleaned_data["logo"]

                company.save()

                return HttpResponseRedirect('/company/view/')
            else:
                return render(request, 'company/company_edit.html', {'form': form, 'errors': errors, 'logo': company.logo})

    else:
        raise PermissionDenied

    return render(request, 'company/company_edit.html', {'form': form, 'logo': company.logo})


@login_required
def view(request):
    """
    Se escoge la comoañía correspondiente al administrador que la ve

    url = company/view

    parameters/returns:
    company: datos de la compañía

    template: company_view.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)
    company = get_object_or_404(Company, cif=admin.company_id.cif)

    return render(request, 'company/company_view.html', {'company': company, 'admin': admin})


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


# Auxiliar methods, containing the operation logic
def create_company(form):
    """
    Creates a company, supposing the data provided by the form is OK
    """
    cif = form.cleaned_data['cif']
    company_name = form.cleaned_data['company_name']
    short_name = form.cleaned_data['short_name']
    email = form.cleaned_data['company_email']
    phone = form.cleaned_data['company_phone']
    logo = form.cleaned_data['logo']

    company = Company.objects.create(cif=cif, company_name=company_name, short_name=short_name,
                                     email=email, phone=phone, logo=logo)
    return company


def register_administrator(form, company):
    """
    Tegisters an administrator for a company, supposing the data provided by the form is OK
    """
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    user_email = form.cleaned_data['admin_email']

    admin = User.objects.create_user(username=username, password=password, email=user_email,
                                     first_name=first_name, last_name=last_name)

    identifier = form.cleaned_data['admin_identifier']
    phone = form.cleaned_data['admin_phone']

    administrator = Administrator.objects.create(user=admin, user_type="A", identifier=identifier,
                                                 phone=phone, company_id=company)
    return administrator


def check_passwords(form):
    """
    checks if two passwords are the same
    """
    return form.cleaned_data['password'] == form.cleaned_data['repeatPassword']


def validate_cif(request):
    """
    checks if the company cif already exist
    """
    cif = request.GET.get('cif')

    check = get_or_none(Company, cif=cif)
    if check is not None:
        check = check.cif

    data = {
        'is_taken': cif == check
    }
    if data['is_taken']:
        data['error_message'] = 'ERROR'
    return JsonResponse(data)


def validate_admin(request):
    """
    checks if the company administrator is registered
    """
    admin = request.GET.get('admin')

    check = get_or_none(Administrator, user__username=admin)
    if check is not None:
        check = check.user.username

    data = {
        'is_taken': admin == check
    }
    if data['is_taken']:
        data['error_message'] = 'ERROR'
    return JsonResponse(data)


def validate_short_name(request):
    """
    checks if the company short name already exist
    """
    short_name = request.GET.get('short_name')

    check = get_or_none(Company, short_name=short_name)
    if check is not None:
        check = check.short_name

    data = {
        'is_taken': short_name == check
    }
    if data['is_taken']:
        data['error_message'] = 'ERROR'
    return JsonResponse(data)


def validate_email(request):
    """
    checks whether the email is unique
    """
    email = request.GET.get("email", None)
    is_taken = not (is_company_email_unique(email) and is_email_unique(email))
    return JsonResponse({'is_taken': is_taken})
