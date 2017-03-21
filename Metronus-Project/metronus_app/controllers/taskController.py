from django.shortcuts import render
from metronus_app.forms.taskForm import TaskForm
from metronus_app.model.task import Task
from django.shortcuts import render_to_response, get_object_or_404
from metronus_app.common_utils import get_current_admin_or_403,get_current_employee_or_403
from django.http import HttpResponseRedirect
from metronus_app.model.administrator import Administrator
from metronus_app.model.actor import Actor
from metronus_app.model.project import Project
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
    actor=checkTask(None,request)

    repeated_name=False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request,request.POST)
        # check whether it's valid:

        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            pname=form.cleaned_data['name']
            ppro=form.cleaned_data['project_id']
            pdep=form.cleaned_data['department_id']
            pdtuple=find_tuple(ppro.id,pdep.id,actor)
            pro=find_name(pname,pdtuple)
            if pro is not None:
                if not pro.active:
                    checkTask(pro,request)
                    pro.active=True
                    pro.save()
                    return HttpResponseRedirect('/task/list')
                else:
                    repeated_name=True
            else:
                actor=checkTask(pro,request)
                createTask(form,pdtuple,actor)
                return HttpResponseRedirect('/task/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaskForm(request,initial={"task_id":0})

    return render(request, 'task_form.html', {'form': form,'repeated_name':repeated_name})


def list(request):
    """
    returns:
    tasks: lista de tareas de la compañía logeada

    template:
    task_list.html
    """
     # Check that the user is logged in
    tasks=checkRoleForList(request)
    return render(request, "task_list.html", {"tasks": tasks})

def view(request,task_id):
    """
    parameters:
    task_id: the task id to delete

    returns:
    task

    template:
    task_view.html
    """
    task=get_object_or_404(Task,pk=task_id)
    tasks=checkRoleForList(request)
    if tasks.filter(pk=task.id).count()==0:
        raise PermissionDenied
    return render(request, "task_view.html", {"task": task})

def edit(request,task_id):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea

    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)
    repeated_name=False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request,request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            task=get_object_or_404(Task,pk=form.cleaned_data['task_id'])
            checkTask(task,request)
            ppro=form.cleaned_data['project_id']
            pdep=form.cleaned_data['department_id']
            pdtuple=find_tuple(ppro.id,pdep.id,actor)
            pro=find_name(form.cleaned_data['name'],pdtuple)
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
        form = TaskForm(request,initial={"name":task.name,"description":task.description,
                "task_id":task.id})

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
    task=get_object_or_404(Task,pk=task_id,active=True)
    checkTask(task,request)
    deleteTask(task)

    return HttpResponseRedirect('/task/list')

#Auxiliar methods, containing the operation logic

def createTask(form, project_department,actor):
    fname=form.cleaned_data['name']
    fdescription=form.cleaned_data['description']
    Task.objects.create(name=fname,description=fdescription,projectDepartment_id=project_department,actor_id=actor)

def updateTask(task,form):
    task.name = form.cleaned_data['name']
    task.description = form.cleaned_data['description']
    task.save()

def deleteTask(task):
    task.active=False
    task.save()

def checkRoleForList(request):
    """
    returns the list depending on the actor
    """
    actor=None
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

    if actor.user_type!='A':
        #not an admin
        isTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name= "Team manager")
        res=isTeamManager.count()>0

        if res:
            #is manager
            task=Task.objects.filter(actor_id__company_id=actor.company_id,active=True)
        else:
            #not a manager
            task=Task.objects.filter(actor_id__company_id=actor.company_id,projectDepartment_id__projectdepartmentemployeerole__employee_id=actor,active=True).distinct()
    else:
        #is admin
        task=Task.objects.filter(actor_id__company_id=actor.company_id,active=True)
    return task
def checkTask(task,request):
    """
    checks if the task belongs to the logged actor with appropiate roles
    Admin, manager or dep/proj manager
    """
    actor=None
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

    # Check that the actor has permission to view the task
    if task is not None and task.actor_id.company_id != actor.company_id:
        raise PermissionDenied

    if actor.user_type!='A':
        isTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name= "Team manager")
        res=isTeamManager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name__in=["Project manager","Coordinator"])
            res=roles.count()>0
        if not res:
            raise PermissionDenied

    return actor
def find_name(pname,projectDepartment):
    """
    Returns whether there is already a task with the tuple project-department
    """
    return Task.objects.filter(name=pname,projectDepartment_id=projectDepartment).first()

def find_tuple(project_id,department_id,actor):
    """
    Returns a tuple project-department
    """
    project=get_object_or_404(Project,pk=project_id)
    department=get_object_or_404(Department,pk=department_id)

    if project.company_id!=department.company_id or  project.company_id!=actor.company_id :
        raise PermissionDenied
    return ProjectDepartment.objects.get(project_id=project,department_id=department)
