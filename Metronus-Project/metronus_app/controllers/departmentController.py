from django.shortcuts import render
from metronus_app.forms.departmentForm import DepartmentForm
from metronus_app.model.department import Department
from metronus_app.model.administrator import Administrator
from populate_database import basicLoad

from django.http import HttpResponseRedirect
from django.core.exceptions             import ObjectDoesNotExist
from django.http                        import HttpResponseForbidden
from django.contrib.auth import authenticate,login

def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento

    template:
    department_form.html
    """
    # Check that the user is logged in
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    # Check that the current user is an administrator
    admin = get_current_admin(request)

    if admin == None:
        return HttpResponseForbidden()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            createDepartment(form,admin)
            return HttpResponseRedirect('/department/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DepartmentForm(initial={"department_id":0})


    return render(request, 'department_form.html', {'form': form})


def list(request):

    """
    returns:
    departments: lista de departamentos de la compañía logeada

    template:
    department_list.html
    """
    # Check that the user is logged in
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    # Check that the current user is an administrator
    admin = get_current_admin(request)

    if admin == None:
        return HttpResponseForbidden()
    lista=Department.objects.filter(company_id=admin.company_id,active=True)
    return render(request, "department_list.html", {"departments": lista})


def update(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento

    template:
    department_form.html
    """
    # Check that the user is logged in
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    # Check that the current user is an administrator
    admin = get_current_admin(request)

    if admin == None:
        return HttpResponseForbidden()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            department=Department.objects.get(pk=form.cleaned_data['department_id'])
            if checkCompanyDepartment(department,admin.company_id):
                updateDepartment(department,form)

            return HttpResponseRedirect('/department/list')

    # if a GET (or any other method) we'll create a blank form
    else:

        department_id=request.GET.get('department_id')
        department=Department.objects.get(pk=department_id)
        form = DepartmentForm(initial={"name":department.name,"department_id":department.id})


    return render(request, 'department_form.html', {'form': form})

def delete(request):
    """
    parameters:
    department_id: the department id to delete

    returns:
    nothing

    template:
    deparment_list.html
    """

    # Check that the user is logged in
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    # Check that the current user is an administrator
    admin = get_current_admin(request)

    if admin == None:
        return HttpResponseForbidden()
    department_id=request.GET.get('department_id')
    department=Department.objects.get(pk=department_id)
    if checkCompanyDepartment(department,admin.company_id):
        deleteDepartment(department)
    return HttpResponseRedirect('/'+request.LANGUAGE_CODE+'/department/list')

#Auxiliar methods, containing the operation logic

def createDepartment(form,admin):
    dname=form.cleaned_data['name']
    company=admin.company_id
    Department.objects.create(name=dname,active=True,company_id=company)

def updateDepartment(department,form):
    department.name = form.cleaned_data['name']
    department.save()

def deleteDepartment(department):
    department.active=False
    department.save()

def checkCompanyDepartmentSession(department,admin):
    """
    checks if the department belongs to the logged company
    """
    return checkCompanyDepartment(department,admin.company_id)
def checkCompanyDepartment(department,company_id):
    """
    checks if the department belongs to the specified company
    """
    return department is not None and company_id==department.company_id and department.active

def checkCompanyDepartmentIdSession(departmentId,admin):
    """
    checks if the department belongs to the logged company
    """
    return checkCompanyDepartmentId(departmentId,admin.company_id)

def checkCompanyDepartmentId(departmentId,companyId):
    """
    checks if the department belongs to the specified company
    """
    department = Department.objects.get(id = departmentId, company_id=companyId, active=True)

    return department is not None
def get_current_admin(request):
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return None
