from django.shortcuts import render
from metronus_app.forms.taskForm import TaskForm
from metronus_app.model.task import Task
from django.shortcuts import render_to_response, get_object_or_404
from metronus_app.common_utils import get_current_admin_or_403,get_current_employee_or_403
from django.http import HttpResponseRedirect
from metronus_app.model.administrator import Administrator
from metronus_app.model.actor import Actor
from metronus_app.model.project import Project
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.employee import Employee
from metronus_app.model.department import Department
from metronus_app.model.goalEvolution import GoalEvolution
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from populate_database import basicLoad
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseForbidden,HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate,login
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse

from datetime import date, timedelta
from django.utils.dateparse import parse_datetime

import re
import calendar


def create(request):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea
    departments:eso
    projects:eso

    errors: una lista con lo siguiente, empezando por task_creation_
    repeated_name: si el nombre es repetido
    invalid_goal:si el objetivo es incorrecto(está uno en blanco y otro no)
    project_department_not_related: si no están relacionados projectdepartment
    invalid_price: si el precio no esta puesto acorde al objetivo de producción (o no es positivo)
    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)
    errors = []

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:

        if form.is_valid():
            # process the data in form.cleaned_data as required
            if not checkGoal(form):
                errors.append('task_creation_invalid_goal')
            if not checkPrice(form):
                errors.append('task_creation_invalid_price')
            
            pname=form.cleaned_data['name']
            ppro=form.cleaned_data['project_id']
            pdep=form.cleaned_data['department_id']
            pdtuple=find_tuple(ppro.id,pdep.id,actor)
            if pdtuple is None:
                errors.append('task_creation_project_department_not_related')
            else:
                pro=find_name(pname,pdtuple)
                if pro is not None and pro.active:
                    errors.append('task_creation_repeated_name')

            if not errors:
                if pro is not None:
                    if not pro.active:
                        checkTask(pro,request)
                        pro.active=True
                        pro.save()
                        return HttpResponseRedirect('/task/list')
                else:
                    actor=checkTask(pro,request)
                    createTask(form,pdtuple,actor)
                    return HttpResponseRedirect('/task/list')
                
    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaskForm()
    coll=find_collections(request)
    return render(request, 'task_form.html', {'form': form,'errors':errors,
        "departments":coll["departments"],"projects":coll["projects"]})


def createAsync(request):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea
    departments:eso
    projects:eso

    errors: una lista con lo siguiente, empezando por task_creation_
    repeated_name: si el nombre es repetido
    invalid_goal:si el objetivo es incorrecto(está uno en blanco y otro no)
    project_department_not_related: si no están relacionados projectdepartment
    invalid_price: si el precio no esta puesto acorde al objetivo de producción (o no es positivo)
    
    success:si tuvo éxito la operación

    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)
    
    errors=[]
    data = {
        'success':True
    }
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:

        if form.is_valid():
            # process the data in form.cleaned_data as required
            if not checkGoal(form):
                errors.append('task_creation_invalid_goal')
            if not checkPrice(form):
                errors.append('task_creation_invalid_price')
            
            pname=form.cleaned_data['name']
            ppro=form.cleaned_data['project_id']
            pdep=form.cleaned_data['department_id']
            pdtuple=find_tuple(ppro.id,pdep.id,actor)
            if pdtuple is None:
                errors.append('task_creation_project_department_not_related')
            else:
                pro=find_name(pname,pdtuple)
                if pro is not None and pro.active:
                    errors.append('task_creation_repeated_name')

            if not errors:
                if pro is not None:
                    if not pro.active:
                        checkTask(pro,request)
                        pro.active=True
                        pro.save()
                        return JsonResponse(data)
                else:
                    actor=checkTask(pro,request)
                    createTask(form,pdtuple,actor)
                    return JsonResponse(data)
    # if a GET (or any other method) we'll create a blank form
    else:
        return HttpResponseRedirect('/department/create')
    data['success']=False
    data['errors']=errors

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
    task:the task
    goal_evolution: the production goal evolution for this task
    productivity: the evolution of productivity for this task

    template:
    task_view.html
    """

    task = get_object_or_404(Task, pk=task_id)
    checkTask(task, request)
    goal_evolution = GoalEvolution.objects.filter(task_id=task.id)
    employees = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__task=task.id).distinct()
  
    return render(request, "task_view.html", {"task": task, "goal_evolution": goal_evolution, "employees": employees})

def edit(request,task_id):
    """
    parameters/returns:
    form: el formulario con los datos de la tarea
    departments:eso
    projects:eso
    
    errors: ver create
    repeated_name: si el nombre es repetido
    invalid_goal:si el objetivo es incorrecto(está uno en blanco y otro no)
    project_department_not_related: si no están relacionados projectdepartment
    invalid_price: si el precio no esta puesto acorde al objetivo de producción (o no es positivo)
   
    template:
    task_form.html
    """
     # Check that the user is logged in
    actor=checkTask(None,request)

    errors=[]
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            if not checkGoal(form):
                errors.append('task_creation_invalid_goal')
            if not checkPrice(form):
                errors.append('task_creation_invalid_price')

            
            task=get_object_or_404(Task,pk=form.cleaned_data['task_id'])
            checkTask(task,request)
            #find tasks with the same name
            pro=Task.objects.filter(name=form.cleaned_data['name'],projectDepartment_id=task.projectDepartment_id).first()

            #pro does not exists or it's the same
            if pro is not None and pro.id!=task.id and pro.active:
                errors.append('task_creation_repeated_name')
            
            if not errors:
                updateTask(task,form,actor)
                return HttpResponseRedirect('/task/list')


    # if a GET (or any other method) we'll create a blank form
    else:
        task=get_object_or_404(Task,pk=task_id)
        form = TaskForm(initial={"name":task.name,"description":task.description,
                "task_id":task.id,
                "production_goal":task.production_goal if task.production_goal is not None else "",
                "goal_description":task.goal_description if task.goal_description is not None else "",
                "project_id":task.projectDepartment_id.project_id,
                "department_id":task.projectDepartment_id.department_id,
                "price_per_unit":task.price_per_unit if task.price_per_unit is not None else "",
                "price_per_hour":task.price_per_hour if task.price_per_hour is not None else ""})
    #The project
    coll=find_collections(request)
    return render(request, 'task_form.html', {'form': form,"errors":errors,
        "departments":coll["departments"],"projects":coll["projects"]})

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

#Métodos para métricas

@login_required
def ajax_productivity_per_task(request):
    """
    # Devuelve un objeto {'names': [dpto1, dpto2...], 'values': [tiempo1, tiempo2...]}

    # Parámetros obligatorios:
    # task_id - ID del task

    # Parámetros opcionales: 
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    """
    # ------------------------- Cortesía de Agu ------------------------------

    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        actor= Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied
        
    if "task_id" not in request.GET:
        return HttpResponseBadRequest()

    task_id = request.GET["task_id"]

    # Get and parse the dates and the offset
    start_date = request.GET.get("start_date", str(date.today()- timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
    date_regex = re.compile("^\d{4}-\d{2}-\d{2}$")

    if date_regex.match(start_date) is None or date_regex.match(end_date) is None:
        return HttpResponseBadRequest("Start/end date are not valid")

    offset = request.GET.get("offset", "+00:00")
    offset_regex = re.compile("^(\+|-)\d{2}:\d{2}$")

    if offset_regex.match(offset) is None:
        return HttpResponseBadRequest("Time offset is not valid")

    # Append time offsets
    start_date += " 00:00" + offset
    end_date += " 00:00" + offset

    # --------------------------------------------------------------------------
    data = {
        'production': [],
        'goal_evolution': [],
        'days':[]
    }
    print(start_date)
    print(end_date)
    production = TimeLog.objects.filter(task_id_id=task_id, workDate__range=[start_date, end_date]).order_by('workDate')
    print(production)
    task = get_object_or_404(Task, pk=task_id, active=True)
    z = 0
    start_date_parse = parse_datetime(start_date)
    for i in range(0, 31):
        if production is not None and len(production) > z and abs((production[z].workDate-start_date_parse).days) == i:
            print('patata')
            data['production'].append(production[z].produced_units / (production[z].duration/60))
            z += 1
        else:
            data['production'].append(0)

        data['goal_evolution'].append(task.production_goal)

        prod_day = start_date_parse + timedelta(days=i)
        data['days'].append(str(prod_day.day)+", "+str(calendar.month_name[prod_day.month]))
    print(data['production'])
    return JsonResponse(data)


#Auxiliar methods, containing the operation logic

def createTask(form, project_department,actor):
    """Creates a task supposing the data in the form is ok"""
    fname=form.cleaned_data['name']
    fdescription=form.cleaned_data['description']
    fgoal=form.cleaned_data['production_goal']
    fgoaldescription=form.cleaned_data['goal_description']
    fperunit=form.cleaned_data['price_per_unit']
    fperhour=form.cleaned_data['price_per_hour']

    task=Task.objects.create(name=fname,description=fdescription,
        projectDepartment_id=project_department,actor_id=actor,
        production_goal=fgoal,goal_description=fgoaldescription,
        price_per_unit=fperunit,price_per_hour=fperhour)

def updateTask(task,form,actor):
    """Updates a task and saves the data in the log"""
    newGoalEntry(task,form,actor)
    task.name = form.cleaned_data['name']
    task.description = form.cleaned_data['description']
    task.production_goal = form.cleaned_data['production_goal']
    task.goal_description = form.cleaned_data['goal_description']
    task.price_per_unit=form.cleaned_data['price_per_unit']
    task.price_per_hour=form.cleaned_data['price_per_hour']
    task.save()

def newGoalEntry(task,form,actor):
    """
    Creates a new entry in the goal production if the parameters were checked
    """
    fgoal=form.cleaned_data['production_goal']
    fgoaldescription=form.cleaned_data['goal_description']
    fperunit=form.cleaned_data['price_per_unit']
    fperhour=form.cleaned_data['price_per_hour']
    if fgoal!=task.production_goal or fgoaldescription!=task.goal_description or \
        fperhour!=task.price_per_hour or fperunit!=task.price_per_unit:
        GoalEvolution.objects.create(task_id  = task,
            actor_id = actor,
            production_goal=task.production_goal,
            goal_description=task.goal_description,
            price_per_unit=task.price_per_unit,
            price_per_hour=task.price_per_hour)

def checkGoal(form):
    """
    This returns true if both goal and description are empty or both are not empty
    """
    fgoal=form.cleaned_data['production_goal']
    fgoaldescription=form.cleaned_data['goal_description']
    return (fgoal!="" and fgoaldescription!="") or (not fgoal and not fgoaldescription)

def checkPrice(form):
    """
    This returns true if the price field is valid
    This means only per_unit or per_hour must be filled 
    and only if there is a valid goal description for the first field, or no goal for the second
    """
    fgoal=form.cleaned_data['production_goal']
    fgoaldescription=form.cleaned_data['goal_description']
    fperunit=form.cleaned_data['price_per_unit']
    fperhour=form.cleaned_data['price_per_hour']
    return (fgoaldescription is not None and fgoaldescription!="" and  fperhour is None and fperunit is not None and fperunit>0 ) or \
        ( (fgoaldescription is None or fgoaldescription=="") and fperunit is None and fperhour is not None and fperhour>0)


def deleteTask(task):
    """Deletes a task"""
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
        is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=is_team_manager.count()>0

        if res:
            #is manager
            task=Task.objects.filter(actor_id__company_id=actor.company_id,active=True).distinct()
        else:
            #not a manager
            task=Task.objects.filter(actor_id__company_id=actor.company_id,projectDepartment_id__projectdepartmentemployeerole__employee_id=actor,active=True).distinct()
    else:
        #is admin
        task=Task.objects.filter(actor_id__company_id=actor.company_id,active=True).distinct()
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
        is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=is_team_manager.count()>0

        if not res:
            roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier__in=[50,40,20])
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
    """
    Gets the projects and departments the logged user can create tasks for, depending to their roles
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
        is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=is_team_manager.count()>0

        if res:
            #is manager
            proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)
            departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
        else:
            #not a manager
            roles_pro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__tier__gte=40)
            roles_dep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__tier=20)

            if  roles_pro.count()>0:
                #you're a project manager. Loading your projects
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor).distinct()
            elif roles_dep.count()>0:
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
    """
    Gets the  departments the logged user can create tasks for a project, depending to their roles
    """
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
        is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=is_team_manager.count()>0

        if res:
            #is manager
            departamentos=Department.objects.filter(company_id=actor.company_id,active=True)
        else:
            #not a manager
            roles_pro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__tier__gte=40)
            roles_dep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__tier=20)

            if  roles_pro.count()>0:
                #you're a project manager. Loading your projects
                departamentos=Department.objects.filter(company_id=actor.company_id,active=True,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor,projectdepartment__project_id_id=project_id).distinct()
            elif roles_dep.count()>0:
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
    """
    Gets the projects and departments the logged user can create tasks for a department, depending to their roles
    """
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
        is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                    role_id__tier= 30)
        res=is_team_manager.count()>0

        if res:
            #is manager
            proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False)

        else:
            #not a manager
            roles_pro = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__tier__gte=40)
            roles_dep=ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                     role_id__tier=20)

            if  roles_pro.count()>0:
                #you're a project manager. Loading your projects
                proyectos=Project.objects.filter(company_id=actor.company_id,deleted=False,
                    projectdepartment__projectdepartmentemployeerole__employee_id=actor
                    ,projectdepartment__department_id_id=department_id).distinct()

            elif roles_dep.count()>0:
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
