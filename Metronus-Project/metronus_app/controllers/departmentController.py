from django.shortcuts import render
from metronus_app.forms.departmentForm import DepartmentForm
from metronus_app.model.department import Department
def create(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento

    template:
    department_form.html
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DepartmentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            createDepartment(form)
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
    lista=Department.objects.filter(company_id=request.session['id'],active=True)
    return render(request, "department_list.html", {"departments": lista})


def update(request):
    """
    parameters/returns:
    form: el formulario con los datos del departamento

    template:
    department_form.html
    """
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
            if checkCompanyDepartment(department):
                updateDepartment(department,form)

            return HttpResponseRedirect('/department/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        department_id=request.GET.get('department_id')
        department=Department.objects.get(pk=department_id)
        form = DepartmentForm(initial={"name":deparment.name,"department_id":department.id})


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
    department_id=request.GET.get('department_id')
    department=Department.objects.get(pk=department_id)
    if checkCompanyDepartment(department):
        deleteDepartment(department)
    return HttpResponseRedirect('/department/list')

#Auxiliar methods, containing the operation logic

def createDepartment(form):
    dname=form.cleaned_data['name']
    company=Company.objects.get(pk=request.session['id'])
    Department.objects.create(name=dname,active=True,company_id=company)

def updateDepartment(department,form):
    department.name = form.cleaned_data['name']
    department.save()

def deleteDepartment(department):
    department.active=False
    department.save()

def checkCompanyDepartmentSession(department):
    """
    checks if the department belongs to the logged company
    """
    return checkCompanyDepartment(department,request.session['id'])
def checkCompanyDepartment(department,company_id):
    """
    checks if the department belongs to the specified company
    """
    return department is not None and company_id==department.company_id and department.active

def checkCompanyDepartmentIdSession(departmentId):
    """
    checks if the department belongs to the logged company
    """
    return checkCompanyDepartmentId(departmentId,request.session['id'])

def checkCompanyDepartmentId(departmentId,companyId):
    """
    checks if the department belongs to the specified company
    """
    department = Department.objects.get(id = departmentId, company_id=companyId, active=True)
    
    return department is not None