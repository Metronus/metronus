from django.shortcuts import render
from metronus_app.forms.departmentForm import DepartmentForm
from metronus_app.model.department import Department
from metronus_app.model.administrator import Administrator
from populate_database import basicLoad
from django.shortcuts                            import render_to_response, get_object_or_404
from metronus_app.common_utils                   import get_current_admin_or_403
from django.http import HttpResponseRedirect
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth import authenticate,login

def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)
    repeated_name=False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            dname=form.cleaned_data['name']
            dep=findName(dname,admin)
            if dep is not None:
                if not dep.active:
                    dep.active=True
                    dep.save()
                    return HttpResponseRedirect('/department/list')
                else:
                    repeated_name=True
            else:
                createDepartment(form,admin)
                return HttpResponseRedirect('/department/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DepartmentForm(initial={"department_id":0,"name":""})


    return render(request, 'department_form.html', {'form': form,'repeated_name':repeated_name})


def list(request):

    """
    returns:
    departments: lista de departamentos de la compañía logeada

    template:
    department_list.html
    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)

    lista=Department.objects.filter(company_id=admin.company_id,active=True)
    return render(request, "department_list.html", {"departments": lista})


def edit(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento
    repeated_name:true si el nombre ya existe para otro departamento

    template:
    department_form.html
    """

    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)
    repeated_name=False

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            department=get_object_or_404(Department,pk=form.cleaned_data['department_id'])
            if checkCompanyDepartment(department,admin.company_id):
                dep=findName(form.cleaned_data['name'],admin)
                #dep does not exists or it's the same
                if dep is None or dep.id==department.id:
                    editDepartment(department,form)
                    return HttpResponseRedirect('/department/list')
                else:
                    if dep.active:
                        repeated_name=True
    # if a GET (or any other method) we'll create a blank form
    else:

        department_id=request.GET.get('department_id')
        department=get_object_or_404(Department,pk=department_id)
        form = DepartmentForm(initial={"name":department.name,"department_id":department.id})


    return render(request, 'department_form.html', {'form': form,'repeated_name':repeated_name})

def delete(request):
    """
    parameters:
    department_id: the department id to delete

    returns:
    nothing

    template:
    deparment_list.html
    """


    # Check that the current user is an administrator
    admin = get_current_admin_or_403(request)

    department_id=request.GET.get('department_id')
    department=get_object_or_404(Department,pk=department_id)
    if checkCompanyDepartment(department,admin.company_id):
        deleteDepartment(department)
<<<<<<< HEAD

=======
>>>>>>> 918bf6dc29681b3935a5fd3cd14066ec31c72543
    return HttpResponseRedirect('/department/list')

#Auxiliar methods, containing the operation logic
def findName(dname,admin):
    return Department.objects.filter(name=dname,company_id=admin.company_id).first()

def createDepartment(form,admin):

    dname=form.cleaned_data['name']
    company=admin.company_id
    Department.objects.create(name=dname,active=True,company_id=company)

def editDepartment(department,form):

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
    res= department is not None and company_id==department.company_id and department.active
    if not res:
        raise PermissionDenied
    return res


def get_current_admin(request):
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return None
