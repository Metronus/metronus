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
from metronus_app.model.department import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from populate_database import basicLoad
from django.core.exceptions             import ObjectDoesNotExist, PermissionDenied
from django.http                        import HttpResponseForbidden
from django.contrib.auth import authenticate,login
from datetime import date,datetime
from metronus_app.model.actor import Actor
import json
from django.http import HttpResponse
import calendar
from django.core import serializers


def list_all(request):
    """
    valid_production_units: devuelve si se especificó production units y es necesario,
    o si no se especificó y no era necesario
    over_day_limit:True si se paso del límite de 1440 horas al día
    """
    valid_production_units=True
    over_day_limit=False
    today = datetime.today()
    employee = get_current_employee_or_403(request)
    if(request.GET.get('currentMonth')):
        currentMonth = int(request.GET['currentMonth'])
    else:
        currentMonth = today.month

    if (request.GET.get('currentYear')):
        currentYear = int(request.GET['currentYear'])
    else:
        currentYear = today.year

    #pa que quieres esto si ya se comprueba como empleado
    try:
        actor = Actor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied


    if request.method == 'POST' and request.is_ajax():
        project = request.POST.get("project")
        department = request.POST.get("department")

        if project=='':
            return
        else:
            if department is None:
                departments = Department.objects.filter(company_id=actor.company_id,
                                                projectdepartment__project_id=project,
                                                projectdepartment__projectdepartmentemployeerole__employee_id=employee).distinct()

                data = serializers.serialize('json', departments, fields=('id','name',))



                return HttpResponse(data)
            else:
                print (department)
                tasks = Task.objects.filter(projectDepartment_id__department_id=department,
                                            projectDepartment_id__project_id=project,active=True).distinct()
                data = serializers.serialize('json', tasks, fields=('id', 'name',))

                return HttpResponse(data)

    if request.method == 'POST':
        form = TimeLogForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            valid_production_units = checkProducedUnits(form)
            over_day_limit=checkDayLimit(form,employee)
            if valid_production_units and not over_day_limit:
                createTimeLog(form, employee)
                return redirect('timeLog_list_all')

    today = datetime.today()


    tareas=Task.objects.filter(actor_id__company_id=actor.company_id,
                                   projectDepartment_id__projectdepartmentemployeerole__employee_id=actor,
                                   active=True).distinct()
    my_tasks = [myTask(x,currentMonth,currentYear) for x in tareas]

    month = [x for x in range(1,calendar.monthrange(currentYear,currentMonth)[1]+1)]
    month.append("Total")
    total = [sum([x.durations[i][0] for x in my_tasks]) for i in range(0,calendar.monthrange(currentYear,currentMonth)[1]) ]
    monthTotal = sum(total)
    total.append(monthTotal)

    form = TimeLog2Form(request, initial={"timeLog_id": 0, "workDate": datetime.now()})

    return render(request, "timeLog/timeLog_list_all.html", {"my_tasks": my_tasks, "month":month,"total":total, "currentMonth":currentMonth, "currentYear":currentYear, 
        "form":form,"valid_production_units":valid_production_units,"over_day_limit":over_day_limit})


#Método para eliminar un registro siempre que la fecha del registro sea la misma que cuando se llama al método
def delete(request, timeLog_id):
    employee = get_current_employee_or_403(request)
    timeLog = findTimeLog(timeLog_id)
    task = timeLog.task_id
    if(employee.id==timeLog.employee_id.id):
        if checkTimeLogOvertime(timeLog):
            timeLog.delete()
            return redirect('timeLog_list_all')
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied
    return redirect('timeLog_list_all')

#Método auxiliar para encontrar una tarea
def findTask(task_id):
    task = get_object_or_404(Task,pk=task_id)
    return task

#Método auxiliar para la creación de registros
def createTimeLog(form, employee):
    fdescription = form.cleaned_data['description']
    fworkDate = form.cleaned_data['workDate']
    if (fworkDate.date() > date.today()):
        raise PermissionDenied
    fduration = form.cleaned_data['duration']
    funits=form.cleaned_data['produced_units']
    task = findTask(form.cleaned_data['task_id'])
    timeLog = findTimeLogByDateAndTask(fworkDate,task)
    if(timeLog is not None):
        timeLog.duration += fduration
        timeLog.produced_units+=funits
        timeLog.description = fdescription
        timeLog.produced_units += funits
        timeLog.save()
    else:
        TimeLog.objects.create(description=fdescription,workDate=fworkDate,duration=fduration,task_id=task,employee_id=employee,produced_units=funits)


def checkProducedUnits(form):
    """
    Comprobación para saber si el empleado debe añadir un objetivo de producción
    """
    task = findTask(form.cleaned_data['task_id'])
    prod_units=form.cleaned_data['produced_units']
    return (prod_units and task.production_goal) or (not prod_units and not task.production_goal)

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
                                                                        role_id__tier=30)
    res = isTeamManager.count() > 0
    if not res:
        roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                             projectDepartment_id=task.projectDepartment_id,
                                                             role_id__tier__in=[50,40,20])
        res = roles.count() > 0
    return res

#Método auxiliar para encontrar un registro
def findTimeLog(timeLog_id):
    timeLog = get_object_or_404(TimeLog,pk=timeLog_id)
    return timeLog

class myTask():
    id = 0
    name = ""
    durations = []

    def __init__(self, task, month, year):
        totalDuration = 0
        self.id = task.id
        today = datetime.today()
        self.name = task.name
        self.durations = [(0,0) for x in range(0,calendar.monthrange(year,month)[1])]
        timeLogs = TimeLog.objects.filter(workDate__year__gte=year,workDate__month__gte=month,
                                     workDate__year__lte=year, workDate__month__lte=month,task_id=task.id)

        for tl in timeLogs:
            index = int(tl.workDate.day)-1
            self.durations[index] = (tl.duration,tl.id)
            totalDuration += tl.duration
        self.durations.append((totalDuration,0))

def findTimeLogByDateAndTask(tDate,task):
    #Vaya churro para comprobar que el dia, el mes y el año sean iguales
    timeLog = TimeLog.objects.filter(workDate__year__gte=tDate.date().year,workDate__month__gte=tDate.date().month,workDate__day__gte=tDate.date().day,
                                     workDate__year__lte=tDate.date().year, workDate__month__lte=tDate.date().month,
                                     workDate__day__lte=tDate.date().day,task_id=task).first()
    return timeLog

def checkTimeLogOvertime(timeLog):
    today = datetime.today()
    result = False
    if(timeLog.registryDate.date().day==today.day and timeLog.registryDate.date().month==today.month and timeLog.registryDate.date().year==today.year):
        result = True
    return result

from django.db.models import Sum
def checkDayLimit(form,employee):
    """
    checks the employee cannot work more than 1440 minutes a day (one day in minutes)
    True if the limit was passed
    """
    tDate = form.cleaned_data['workDate']
    time_sum=TimeLog.objects.filter(employee_id=employee,
        workDate__year=tDate.date().year,
        workDate__month=tDate.date().month,
        workDate__day=tDate.date().day).aggregate(current_sum=Sum("duration"))
    current_sum=time_sum["current_sum"] if time_sum["current_sum"] is not None else 0
    return form.cleaned_data["duration"]+current_sum>1440