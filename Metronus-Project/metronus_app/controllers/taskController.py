from django.shortcuts import render
from metronus_app.forms.taskForm import TaskForm
from metronus_app.model.task import Task
from django.shortcuts import render_to_response, get_object_or_404
from metronus_app.common_utils import get_current_admin_or_403,get_current_employee_or_403
from django.http import HttpResponseRedirect
from metronus_app.model.administrator import Administrator
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from populate_database import basicLoad
from django.core.exceptions             import ObjectDoesNotExist, PermissionDenied
from django.http                        import HttpResponseForbidden
from django.contrib.auth import authenticate,login



def create(request):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea

    template:
    task_form.html
    """
     # Check that the user is logged in
    employee = get_current_employee_or_403(request)

    repeated_name=False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            pname=form.cleaned_data['name']
            ppro=form.cleaned_data['project_id']
            pdep=form.cleaned_data['department_id']
            pdtuple=find_tuple(project_id,department_id,employee)
            pro=find_name(pname,pdtuple)
            if pro is not None:
                if not pro.active:
                    checkTask(pro,employee)
                    pro.active=True
                    pro.save()
                    return HttpResponseRedirect('/task/list')
                else:
                    repeated_name=True
            else:
                checkTask(pro,employee)
                createTask(form,pdtuple,employee)
                return HttpResponseRedirect('/task/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaskForm(initial={"task_id":0})

    return render(request, 'task_form.html', {'form': form,'repeated_name':repeated_name})


def list_project(request):
    """
    returns:
    tasks: lista de tareas de la compañía logeada

    template:
    task_list.html
    """
     # Check that the user is logged in
    employee = get_current_employee_or_403(request)
    project_id=request.GET.get("project_id")
    checkRoleForList(employee,project_id,True)
    lista=Task.objects.filter(active=True, projectDepartment_id__project_id__id=project_id)
    return render(request, "task_list.html", {"tasks": lista})
def list_department(request):
    """
    returns:
    tasks: lista de tareas de la compañía logeada

    template:
    task_list.html
    """
     # Check that the user is logged in
    employee = get_current_employee_or_403(request)
    department_id=request.GET.get("department_id")
    checkRoleForList(employee,department_id,False)
    lista=Task.objects.filter(active=True, projectDepartment_id__department_id__id=department_id)
    print(Task.objects.filter(active=True, projectDepartment_id__department_id__id=department_id).values())
    print (Department.objects.filter(projectdepartment__id=2).values())
    return render(request, "task_list.html", {"tasks": lista})


def edit(request,task_id):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea

    template:
    task_form.html
    """
     # Check that the user is logged in
    employee = get_current_employee_or_403(request)
    repeated_name=False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            task=get_object_or_404(Task,pk=form.cleaned_data['task_id'])
            checkTask(task,employee)
            pro=find_name(form.cleaned_data['name'],employee)
            #pro does not exists or it's the same
            if pro is None or pro.id==task.id:
                updateTask(task,form)
                return HttpResponseRedirect('/task/list')
            else:
                if pro.active:
                    repeated_name=True

    # if a GET (or any other method) we'll create a blank form
    else:
        task=get_object_or_404(Task,pk=task_id)
        form = TaskForm(initial={"name":task.name,"description":task.description,
                "task_id":task.id,"project_id":task.projectDepartment_id.project_id,
                "department_id":task.projectDepartment_id.department_id})

    return render(request, 'task_form.html', {'form': form,'repeated_name':repeated_name})

def delete(request,task_id):
    """
    parameters:
    task_id: the task id to delete

    returns:
    nothing

    template:
    task_list.html
    """
     # Check that the user is logged in
    employee = get_current_employee_or_403(request)
    task=get_object_or_404(Task,pk=task_id,active=True)
    checkTask(task,employee)
    deleteTask(task)

    return HttpResponseRedirect('/task/list')

#Auxiliar methods, containing the operation logic

def createTask(form, project_department,employee):
    fname=form.cleaned_data['name']
    fdescription=form.cleaned_data['description']
    Task.objects.create(name=fname,description=fdescription,projectDepartment_id=project_department,actor_id=employee)

def updateTask(task,form):
    task.name = form.cleaned_data['name']
    task.description = form.cleaned_data['description']
    task.save()

def deleteTask(task):
    task.active=False
    task.save()

def checkRoleForList(employee,d_id,projectOrDepartment):
    """
    projectOrDepartment: True if project, false if department
    """
    isAdminOrTeamManager= ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                role_id__name__in=["Administrator" , "Team manager"])
    res=isAdminOrTeamManager.count()>0

    if not res:
        if projectOrDepartment:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                    projectDepartment_id__project_id__id=d_id)
        else:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                    projectDepartment_id__department_id__id=d_id)

        res=roles.count()>0
    if not res:
        raise PermissionDenied

def checkTask(task,employee):
    """
    checks if the task belongs to the logged actor with appropiate roles
    TODO:
    """
    isAdminOrTeamManager= ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                role_id__name__in=["Administrator" , "Team manager"])
    res=isAdminOrTeamManager.count()>0
    if not res:
        roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                projectDepartment_id=task.projectDepartment_id, role_id__name__in=["Project manager","Department manager","Coordinator"])
        res=roles.count()>0
    if not res:
        raise PermissionDenied

def find_name(pname,projectDepartment):
    """
    Returns whether there is already a task with the tuple project-department
    """
    return Task.objects.filter(name=pname,projectDepartment_id=projectDepartment).first()

def find_tuple(project_id,department_id,employee):
    """
    Returns a tuple project-department
    """
    project=get_object_or_404(Project,pk=project_id)
    department=get_object_or_404(Department,pk=department_id)

    if project.company_id!=department.company_id or  project.company_id!=employee.company_id :
        raise PermissionDenied
    return ProjectDepartment.objects.filter(project_id=project,department_id=department)
