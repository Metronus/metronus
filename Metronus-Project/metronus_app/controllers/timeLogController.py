from django.shortcuts import render, redirect
from metronus_app.forms.timeLog2Form import TimeLog2Form
from metronus_app.model.task import Task
from django.shortcuts import get_object_or_404
from metronus_app.common_utils import get_current_employee_or_403
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.department import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.core.exceptions import PermissionDenied

from datetime import date, datetime
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
    valid_production_units = True
    over_day_limit = False
    has_permissions = True
    today = datetime.today()
    employee = get_current_employee_or_403(request)
    if request.GET.get('currentMonth'):
        current_month = int(request.GET['currentMonth'])
    else:
        current_month = today.month

    if request.GET.get('currentYear'):
        current_year = int(request.GET['currentYear'])
    else:
        current_year = today.year

    if request.method == 'POST' and request.is_ajax():
        project = request.POST.get("project")
        department = request.POST.get("department")

        if project == '':
            return
        else:
            if department is None:
                departments = Department.objects.filter(company_id=employee.company_id,
                                                        projectdepartment__project_id=project,
                                                        projectdepartment__projectdepartmentemployeerole__employee_id=employee, active=True).distinct()

                data = serializers.serialize('json', departments, fields=('id', 'name',))

                return HttpResponse(data)
            else:
                print(department)
                tasks = Task.objects.filter(projectDepartment_id__department_id=department,
                                            projectDepartment_id__project_id=project, active=True).distinct()
                data = serializers.serialize('json', tasks, fields=('id', 'name', 'goal_description'))
                return HttpResponse(data)

    if request.method == 'POST':
        form = TimeLog2Form(request, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # extra validations for error messages
            has_permissions = check_permission_for_task(employee, find_task(form.cleaned_data['task_id']))
            valid_production_units = check_produced_units(form)
            over_day_limit = check_day_limit(form, employee)
            if has_permissions and valid_production_units and not over_day_limit:
                create_time_log(form, employee)
                return redirect('timeLog_list_all')
    else:
        form = TimeLog2Form(request, initial={"timeLog_id": 0, "workDate": today})

    tareas = Task.objects.filter(actor_id__company_id=employee.company_id,
                                 projectDepartment_id__projectdepartmentemployeerole__employee_id=employee,
                                 active=True).distinct()
    my_tasks = [MyTask(x, current_month, current_year, employee) for x in tareas]

    month = [x for x in range(1, calendar.monthrange(current_year, current_month)[1]+1)]
    month.append("Total")
    total = [sum([x.durations[i][0] for x in my_tasks]) for i in range(0, calendar.monthrange(current_year, current_month)[1])]
    month_total = sum(total)
    total.append(month_total)

    return render(request, "timeLog/timeLog_list_all.html", {"my_tasks": my_tasks, "month": month, "total": total, "currentMonth": current_month, "currentYear": current_year,
                                                             "form": form, "valid_production_units": valid_production_units, "over_day_limit": over_day_limit, 'has_permissions': has_permissions})


def delete(request, time_log_id):
    """
    Método para eliminar un registro siempre que la fecha del registro sea la misma que cuando se llama al método
    """
    employee = get_current_employee_or_403(request)
    time_log = find_time_log(time_log_id)
    if employee.id == time_log.employee_id.id:
        if check_time_log_overtime(time_log):
            time_log.delete()
            return redirect('timeLog_list_all')
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied
    return redirect('timeLog_list_all')


def find_task(task_id):
    """
    Método auxiliar para encontrar una tarea
    """
    task = get_object_or_404(Task, pk=task_id.id)
    return task


def create_time_log(form, employee):
    """
    Método auxiliar para la creación de registros
    """
    fdescription = form.cleaned_data['description']
    fwork_date = form.cleaned_data['workDate']
    if fwork_date.date() > date.today():
        raise PermissionDenied
    fduration = form.cleaned_data['duration']
    funits = form.cleaned_data['produced_units']
    task = find_task(form.cleaned_data['task_id'])
    time_log = find_time_log_by_date_and_task(fwork_date, task, employee)
    if time_log is not None:
        time_log.duration += fduration
        time_log.description = fdescription

        if time_log.produced_units is None or time_log.produced_units == "":
            time_log.produced_units = funits
        else:
            time_log.produced_units += funits
        time_log.save()
    else:
        TimeLog.objects.create(description=fdescription, workDate=fwork_date, duration=fduration,
                               task_id=task, employee_id=employee, produced_units=funits)


def check_produced_units(form):
    """
    Comprobación para saber si el empleado debe añadir un objetivo de producción
    """
    task = find_task(form.cleaned_data['task_id'])
    prod_units = form.cleaned_data['produced_units']
    # both null or empty OR both not null or empty
    return (prod_units is not None and prod_units != "" and task.production_goal is not None and task.production_goal != "") or ((prod_units is None or prod_units == "") and (task.production_goal is None or task.production_goal == ""))


def check_permission_for_task(employee, task):
    """
    Comprobación para saber si el empleado puede imputar horas
    """
    if employee is not None and task is not None:
        res = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                           projectDepartment_id=task.projectDepartment_id)
        return res.count() > 0
    return False
    

def check_role_for_task(employee, task):
    """Comprobacion para saber si el empleado es un mando superior y
    tiene acceso a todas las imputaciones de una tarea"""

    is_team_manager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                                   role_id__tier=30)
    res = is_team_manager.count() > 0
    if not res:
        roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                             projectDepartment_id=task.projectDepartment_id,
                                                             role_id__tier__in=[50, 40, 20])
        res = roles.count() > 0
    return res


# Método auxiliar para encontrar un registro
def find_time_log(time_log_id):
    time_log = get_object_or_404(TimeLog, pk=time_log_id)
    return time_log


class MyTask:
    """
    This class holds data for timelogs from an employee
    """
    id = 0
    name = ""
    durations = []

    def __init__(self, task, month, year, employee):
        total_duration = 0
        self.id = task.id
        self.name = task.name
        self.durations = [(0, 0) for _ in range(0, calendar.monthrange(year, month)[1])]
        time_logs = TimeLog.objects.filter(workDate__year__gte=year,
                                           workDate__month__gte=month,
                                           workDate__year__lte=year,
                                           workDate__month__lte=month,
                                           task_id=task.id,
                                           employee_id=employee)

        for tl in time_logs:
            index = int(tl.workDate.day)-1
            self.durations[index] = (tl.duration, tl.id)
            total_duration += tl.duration
        self.durations.append((total_duration, 0))


def find_time_log_by_date_and_task(time_log_date, task, employee):
    """Vaya churro para comprobar que el dia, el mes y el año sean iguales"""
    time_log = TimeLog.objects.filter(workDate__year=time_log_date.date().year,
                                      workDate__month=time_log_date.date().month,
                                      workDate__day=time_log_date.date().day,
                                      task_id=task,
                                      employee_id=employee).first()
    return time_log


def check_time_log_overtime(time_log):
    """
    Checks we can edit the timelog, which happens if the last edit for that timelog was today
    """
    today = datetime.today()
    result = False
    if time_log.registryDate.date().day == today.day and time_log.registryDate.date().month == today.month and time_log.registryDate.date().year == today.year:
        result = True
    return result


def check_day_limit(form, employee):
    """
    checks the employee cannot work more than 1440 minutes a day (one day in minutes)
    True if the limit was passed
    """
    t_date = form.cleaned_data['workDate']
    time_sum = TimeLog.objects.filter(employee_id=employee,
                                      workDate__year=t_date.date().year,
                                      workDate__month=t_date.date().month,
                                      workDate__day=t_date.date().day).aggregate(current_sum=Sum("duration"))
    current_sum = time_sum["current_sum"] if time_sum["current_sum"] is not None else 0
    return form.cleaned_data["duration"]+current_sum > 1440 or form.cleaned_data["duration"]+current_sum <= 0
