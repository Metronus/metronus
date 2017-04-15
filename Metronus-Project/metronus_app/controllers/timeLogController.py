from django.shortcuts import render,redirect
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
from django.db.models import Sum

def list_all(request):
    """
    valid_production_units: devuelve si se especificó production units y es necesario,
    o si no se especificó y no era necesario
    over_day_limit:True si se paso del límite de 1440 horas al día
    hasPermissions:True si estas imputando una tarea que es tuya, False si no estas autorizado
    """
    valid_production_units=True
    over_day_limit=False
    has_permissions=True
    today = datetime.today()
    employee = get_current_employee_or_403(request)
    if(request.GET.get('currentMonth')):
        current_month = int(request.GET['currentMonth'])
    else:
        current_month = today.month

    if (request.GET.get('currentYear')):
        current_year = int(request.GET['currentYear'])
    else:
        current_year = today.year

    if request.method == 'POST' and request.is_ajax():
        project = request.POST.get("project")
        department = request.POST.get("department")

        if project=='':
            return
        else:
            if department is None:
                departments = Department.objects.filter(company_id=employee.company_id,
                                                projectdepartment__project_id=project,
                                                projectdepartment__projectdepartmentemployeerole__employee_id=employee,active=True).distinct()

                data = serializers.serialize('json', departments, fields=('id','name',))



                return HttpResponse(data)
            else:
                print (department)
                tasks = Task.objects.filter(projectDepartment_id__department_id=department,
                                            projectDepartment_id__project_id=project,active=True).distinct()
                data = serializers.serialize('json', tasks, fields=('id', 'name','goal_description'))
                return HttpResponse(data)

    if request.method == 'POST':
        form = TimeLog2Form(request,request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #extra validations for error messages
            has_permissions=checkPermissionForTask(employee, findTask(form.cleaned_data['task_id']))
            valid_production_units = checkProducedUnits(form)
            over_day_limit=checkDayLimit(form,employee)
            if has_permissions and valid_production_units and not over_day_limit:
                createTimeLog(form, employee)
                return redirect('timeLog_list_all')
    else:
        form = TimeLog2Form(request, initial={"timeLog_id": 0, "workDate": today})


    tareas=Task.objects.filter(actor_id__company_id=employee.company_id,
                                   projectDepartment_id__projectdepartmentemployeerole__employee_id=employee,
                                   active=True).distinct()
    my_tasks = [MyTask(x,current_month,current_year,employee) for x in tareas]

    month = [x for x in range(1,calendar.monthrange(current_year,current_month)[1]+1)]
    month.append("Total")
    total = [sum([x.durations[i][0] for x in my_tasks]) for i in range(0,calendar.monthrange(current_year,current_month)[1]) ]
    month_total = sum(total)
    total.append(month_total)

    

    return render(request, "timeLog/timeLog_list_all.html", {"my_tasks": my_tasks, "month":month,"total":total, "currentMonth":current_month, "currentYear":current_year, 
        "form":form,"valid_production_units":valid_production_units,"over_day_limit":over_day_limit,'has_permissions':has_permissions})


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
    task = get_object_or_404(Task,pk=task_id.id)
    return task

#Método auxiliar para la creación de registros
def createTimeLog(form, employee):
    fdescription = form.cleaned_data['description']
    fwork_date = form.cleaned_data['workDate']
    if (fwork_date.date() > date.today()):
        raise PermissionDenied
    fduration = form.cleaned_data['duration']
    funits=form.cleaned_data['produced_units']
    task = findTask(form.cleaned_data['task_id'])
    timeLog = findTimeLogByDateAndTask(fwork_date,task,employee)
    if(timeLog is not None):
        timeLog.duration += fduration
        timeLog.description = fdescription

        if timeLog.produced_units is None or timeLog.produced_units=="":
            timeLog.produced_units = funits
        else:
            timeLog.produced_units += funits
        timeLog.save()
    else:
        TimeLog.objects.create(description=fdescription,workDate=fwork_date,duration=fduration,task_id=task,employee_id=employee,produced_units=funits)


def checkProducedUnits(form):
    """
    Comprobación para saber si el empleado debe añadir un objetivo de producción
    """
    task = findTask(form.cleaned_data['task_id'])
    prod_units=form.cleaned_data['produced_units']
    # both null or empty OR both not null or empty
    return (prod_units is not None and prod_units!="" and task.production_goal is not None and task.production_goal!="" ) or ((prod_units is None or prod_units=="") and (task.production_goal is None or task.production_goal==""))

#Comprobación para saber si el empleado puede imputar horas
def checkPermissionForTask(employee, task):
    if employee is not None and task is not None:
        res = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee, projectDepartment_id=task.projectDepartment_id)
        return res.count()>0
    return False
    

#Comprobacion para saber si el empleado es un mando superior y tiene acceso a todas las imputaciones de una tarea
def checkRoleForTask(employee, task):
    is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                                        role_id__tier=30)
    res = is_team_manager.count() > 0
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

class MyTask():
    id = 0
    name = ""
    durations = []

    def __init__(self, task, month, year,employee):
        total_duration = 0
        self.id = task.id
        today = datetime.today()
        self.name = task.name
        self.durations = [(0,0) for x in range(0,calendar.monthrange(year,month)[1])]
        timeLogs = TimeLog.objects.filter(workDate__year__gte=year,workDate__month__gte=month,
                                     workDate__year__lte=year, workDate__month__lte=month,task_id=task.id,employee_id=employee)

        for tl in timeLogs:
            index = int(tl.workDate.day)-1
            self.durations[index] = (tl.duration,tl.id)
            total_duration += tl.duration
        self.durations.append((total_duration,0))

def findTimeLogByDateAndTask(tDate,task,employee):
    #Vaya churro para comprobar que el dia, el mes y el año sean iguales
    timeLog = TimeLog.objects.filter(workDate__year=tDate.date().year,
                                     workDate__month=tDate.date().month,
                                     workDate__day=tDate.date().day,task_id=task,employee_id=employee).first()
    return timeLog

def checkTimeLogOvertime(timeLog):
    today = datetime.today()
    result = False
    if(timeLog.registryDate.date().day==today.day and timeLog.registryDate.date().month==today.month and timeLog.registryDate.date().year==today.year):
        result = True
    return result


def checkDayLimit(form,employee):
    """
    checks the employee cannot work more than 1440 minutes a day (one day in minutes)
    True if the limit was passed
    """
    t_date = form.cleaned_data['workDate']
    time_sum=TimeLog.objects.filter(employee_id=employee,
        workDate__year=t_date.date().year,
        workDate__month=t_date.date().month,
        workDate__day=t_date.date().day).aggregate(current_sum=Sum("duration"))
    current_sum=time_sum["current_sum"] if time_sum["current_sum"] is not None else 0
    return form.cleaned_data["duration"]+current_sum>1440 or form.cleaned_data["duration"]+current_sum<=0