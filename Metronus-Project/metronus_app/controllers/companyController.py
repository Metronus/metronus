from metronus_app.forms.companyForm import CompanyRegistrationForm
from metronus_app.model.company import Company
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import JsonResponse

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.context import RequestContext


def create(request):
    print("create")
    """
    parameters/returns:
    form: el formulario con los datos de la compañía y el administrador de la compañía

    template:
    company_form.html
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CompanyRegistrationForm(request.POST)
        # check whether it's valid:
        print("lets check")
        if form.is_valid() and checkPasswords(form):
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print("ES valido")
            company = createCompany(form)
            registerAdministrator(form, company)
            return HttpResponseRedirect(reverse('login'))

    # if a GET (or any other method) we'll create a blank form
    else:
        # form = DepartmentForm(initial={"department_id":0})
        form = CompanyRegistrationForm()
    return render(request,'company_register.html', {'form': form})


#Auxiliar methods, containing the operation logic

def createCompany(form):
    cif=form.cleaned_data['cif']
    company_name = form.cleaned_data['company_name']
    short_name = form.cleaned_data['short_name']
    email = form.cleaned_data['company_email']
    phone = form.cleaned_data['company_phone']
    #logo = form.cleaned_data['logo']

    company = Company.objects.create(cif=cif, company_name=company_name, short_name=short_name, email=email, phone=phone)
    return company


def registerAdministrator(form, company):
    username = form.cleaned_data['username']
    password = form.cleaned_data['password1']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']

    admin = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)

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
    if cif != "1234":
        raise ValidationError("Email already exists")
    data = {
        'is_taken': cif != "1234"
    }
    return JsonResponse(data)