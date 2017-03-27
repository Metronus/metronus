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
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse

def create(request):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea
    departments:eso
    projects:eso
    repeated_name: si el nombre es repetido
    project_department_related: si nos están relacionados projectdepartment

    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)

    project_department_related=True
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
            pdtuple=find_tuple(ppro.id,pdep.id,actor)
            if pdtuple is not None:
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
            else:
                project_department_related=False
    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaskForm(initial={"task_id":0,"name":"","description":""})
    coll=find_collections(request)
    return render(request, 'task_form.html', {'form': form,'repeated_name':repeated_name,'project_department_related':project_department_related
        ,"departments":coll["departments"],"projects":coll["projects"]})


def createAsync(request):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea
    departments:eso
    projects:eso
    repeated_name: si el nombre es repetido
    project_department_related: si nos están relacionados projectdepartment

    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)
    data = {
        'repeated_name': False,
        'success':True,
        'project_department_related':True
    }

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
            pdtuple=find_tuple(ppro.id,pdep.id,actor)
            if pdtuple is not None:
                pro=find_name(pname,pdtuple)
                if pro is not None:
                    if not pro.active:
                        checkTask(pro,request)
                        pro.active=True
                        pro.save()
                        return JsonResponse(data)
                    else:
                        data['repeated_name']=True
                else:
                    actor=checkTask(pro,request)
                    createTask(form,pdtuple,actor)
                    return JsonResponse(data)
            else:
                data['project_department_related']=False
    # if a GET (or any other method) we'll create a blank form
    else:
        return HttpResponseRedirect('/department/create')
    data['success']=False
    return JsonResponse(data)
def form_projects(request):
    """
    parameters:
    department_id: el departamento asociado
    returns:
    projects: lista de proyectos del actor logeada
    """
    response = serializers.serialize("json", find_projects(request))
    return HttpResponse(response, content_type='application/json')

def form_departments(request):
    """
    parameters:
    project_id: el proyecto asociado
    returns:
    departments :la lista de departamentos
    """
    response = serializers.serialize("json", find_departments(request))
    return HttpResponse(response, content_type='application/json')

def list(request):
    """
    returns:
    tasks: lista de tareas del actor logeado

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
    departments:eso
    projects:eso
    repeated_name: si el nombre es repetido
    project_department_related: si nos están relacionados projectdepartment

    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)
    repeated_name=False
    project_department_related=True
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
            checkTask(task,request)
            #find tasks with the same name
            pro=Task.objects.filter(name=form.cleaned_data['name'],projectDepartment_id=task.projectDepartment_id).first()
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
                "task_id":task.id})
    coll=find_collections(request)
    return render(request, 'task_form.html', {'form': form,'repeated_name':repeated_name,'project_department_related':project_department_related
        ,"departments":coll["departments"],"projects":coll["projects"]})

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
                    role_id__name= "TEAM_MANAGER")
        res=isTeamManager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__name__in=["PROJECT_MANAGER","COORDINATOR"])
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
    return ProjectDepartment.objects.filter(project_id=project,department_id=department).first()


def find_collections(request):
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
                    role_id__name= "TEAM_MANAGER")
        res=isTeamManager.count()>0

        if res:
            #is manager
            proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)
            departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
        else:
            #not a manager
            rolesPro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__name="PROJECT_MANAGER")
            rolesDep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__name="COORDINATOR")

            if  rolesPro.count()>0:
                #you're a project manager. Loading your projects
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
            elif rolesDep.count()>0:
                #you're a department coordinator. loading your departments
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
            else:
                #not any of this? get outta here!!
                raise PermissionDenied
    else:
        #is admin
        proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)
        departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
    return {"departments":departamentos,"projects":proyectos}


def find_departments(request):
    project_id=request.GET.get("project_id")
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
                    role_id__name= "TEAM_MANAGER")
        res=isTeamManager.count()>0

        if res:
            #is manager
            departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
        else:
            #not a manager
            rolesPro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__name="PROJECT_MANAGER")
            rolesDep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__name="COORDINATOR")

            if  rolesPro.count()>0:
                #you're a project manager. Loading your projects
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor,projectdepartment__project_id_id=project_id).distinct()
            elif rolesDep.count()>0:
                #you're a department coordinator. loading your departments
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor,projectdepartment__project_id_id=project_id).distinct()
            else:
                #not any of this? get outta here!!
                raise PermissionDenied
    else:
        #is admin

        departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
    return departamentos

def find_projects(request):
    department_id=request.GET.get("department_id")
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
                    role_id__name= "TEAM_MANAGER")
        res=isTeamManager.count()>0

        if res:
            #is manager
            proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)

        else:
            #not a manager
            rolesPro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__name="PROJECT_MANAGER")
            rolesDep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__name="COORDINATOR")

            if  rolesPro.count()>0:
                #you're a project manager. Loading your projects
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor
                    ,projectdepartment__department_id_id=department_id).distinct()

            elif rolesDep.count()>0:
                #you're a department coordinator. loading your departments
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor
                    ,projectdepartment__department_id_id=department_id).distinct()

            else:
                #not any of this? get outta here!!
                raise PermissionDenied
    else:
        #is admin
        proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)

    return proyectos
