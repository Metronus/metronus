from django.shortcuts import render,redirect
from metronus_app.forms.timeLogForm import TimeLogForm
from metronus_app.forms.timeLog2Form import TimeLog2Form
from metronus_app.model.task import Task
from django.shortcuts import render_to_response, get_object_or_404
from metronus_app.common_utils import get_current_admin_or_403,get_current_employee_or_403
from django.http import HttpResponseRedirect
from metronus_app.model.administrator import Administrator
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from populate_database import basicLoad
from django.core.exceptions             import ObjectDoesNotExist, PermissionDenied
from django.http                        import HttpResponseForbidden
from django.contrib.auth import authenticate,login
from datetime import date,datetime
from metronus_app.model.actor import Actor
import calendar

def create_all(request):
    employee = get_current_employee_or_403(request)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TimeLog2Form(request, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            task = form.cleaned_data['task_id']
            if task is not None:
                createTimeLog(form,task,employee)
                return redirect('timeLog_list_all')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TimeLog2Form(request,initial={"timeLog_id":0, "workDate":datetime.now()})


    return render(request, 'timeLog/timeLog_form.html', {'form': form})

def create_by_task(request,task_id):
    employee = get_current_employee_or_403(request)
    task = findTask(task_id)
    checkPermissionForTask(employee,task)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TimeLogForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if task is not None:
                createTimeLog(form,task,employee)
                return redirect('timeLog_list',task_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TimeLogForm(initial={"timeLog_id":0, "task_id":task_id, "workDate":datetime.now()})


    return render(request, 'timeLog/timeLog_form.html', {'form': form})


def list(request, task_id):
    employee = get_current_employee_or_403(request)
    task = findTask(task_id)
    checkPermissionForTask(employee, task)
    if(checkRoleForTask(employee,task)):
        lista = TimeLog.objects.filter(task_id=task_id) #Mando superior: Puede ver las imputaciones de cualquiera en esa tarea
    else:
        lista = TimeLog.objects.filter(task_id=task_id, employee_id=employee.id) #Empleado normal: Solo puede ver sus imputaciones en esa tarea
    return render(request, "timeLog/timeLog_list.html", {"timeLogs": lista,"task":task})

def list_all(request):
    today = datetime.today()


    try:
        actor = Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied
    tareas=Task.objects.filter(actor_id__company_id=actor.company_id,
                                   projectDepartment_id__projectdepartmentemployeerole__employee_id=actor,
                                   active=True).distinct()
    my_tasks = [myTask(x) for x in tareas]
    month = [x for x in range(1,calendar.monthrange(today.year,today.month)[1]+1)]
    total = [sum([x.durations[i] for x in my_tasks]) for i in range(0,calendar.monthrange(today.year,today.month)[1]) ]
    monthTotal = sum(total)
    return render(request, "timeLog/timeLog_list_all.html", {"my_tasks": my_tasks, "month":month,"total":total, "monthTotal":monthTotal})

def edit(request, timeLog_id):
    employee = get_current_employee_or_403(request)
    timeLog = findTimeLog(timeLog_id)
    if(employee.id==timeLog.employee_id.id):
        if request.method == 'POST':
            form = TimeLogForm(request.POST)
            if form.is_valid():
                log = get_object_or_404(TimeLog,pk=form.cleaned_data['timeLog_id'])
                updateTimeLog(log,form)
                return redirect('timeLog_list',timeLog.task_id.id)
        else:
            log = get_object_or_404(TimeLog, pk=timeLog.id)
            form = TimeLogForm(initial={"description":log.description,"duration":log.duration,
                                        "workDate":log.workDate,"timeLog_id":log.id,"task_id":log.task_id.id})
    else:
        raise PermissionDenied
    return render (request, 'timeLog/timeLog_form.html', {'form': form})

#Método para eliminar un registro siempre que la fecha del registro sea la misma que cuando se llama al método
def delete(request, timeLog_id):
    employee = get_current_employee_or_403(request)
    timeLog = findTimeLog(timeLog_id)
    task = timeLog.task_id
    if(employee.id==timeLog.employee_id.id):
        if(timeLog.registryDate.date() < date.today()):
            raise PermissionDenied
        else:
            timeLog.delete()
            return redirect('timeLog_list',task.id)
    else:
        raise PermissionDenied
    if (checkRoleForTask(employee, task)):
        lista = TimeLog.objects.filter(
            task_id=task.id)  # Mando superior: Puede ver las imputaciones de cualquiera en esa tarea
    else:
        lista = TimeLog.objects.filter(task_id=task.id,
                                       employee_id=employee.id)  # Empleado normal: Solo puede ver sus imputaciones en esa tarea
    return render(request, "timeLog/timeLog_list.html", {"timeLogs": lista, "task": task})

#Método auxiliar para encontrar una tarea
def findTask(task_id):
    task = get_object_or_404(Task,pk=task_id)
    return task

#Método auxiliar para la creación de registros
def createTimeLog(form, task, employee):
    fdescription = form.cleaned_data['description']
    fworkDate = form.cleaned_data['workDate']
    fduration = form.cleaned_data['duration']
    TimeLog.objects.create(description=fdescription,workDate=fworkDate,duration=fduration,task_id=task,employee_id=employee)


#Comprobación para saber si el empleado puede imputar horas
def checkPermissionForTask(employee, task):
    if employee is not None and task is not None:
        res = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee, projectDepartment_id=task.projectDepartment_id)
        if res.count()>0:
            return res
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied

#Comprobacion para saber si el empleado es un mando superior y tiene acceso a todas las imputaciones de una tarea
def checkRoleForTask(employee, task):
    isTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                                        role_id__name="Team manager")
    res = isTeamManager.count() > 0
    if not res:
        roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                             projectDepartment_id=task.projectDepartment_id,
                                                             role_id__name__in=["Project manager",
                                                                                "Coordinator"])
        res = roles.count() > 0
    return res

#Método auxiliar para encontrar un registro
def findTimeLog(timeLog_id):
    timeLog = get_object_or_404(TimeLog,pk=timeLog_id)
    return timeLog

def updateTimeLog(timeLog,form):
    if(timeLog.registryDate.date() < date.today()):
        raise PermissionDenied
    else:
        timeLog.description = form.cleaned_data['description']
        timeLog.workDate = form.cleaned_data['workDate']
        timeLog.duration = form.cleaned_data['duration']
        timeLog.save()

class myTask():
    name = ""
    durations = []

    def __init__(self, task):
        today = datetime.today()
        self.name = task.name
        self.durations = [0 for x in range(0,calendar.monthrange(today.year,today.month)[1])]

        for tl in task.timelog_set.all():
            index = int(tl.workDate.day)
            self.durations[index] += tl.duration