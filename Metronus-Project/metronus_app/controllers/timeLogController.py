from django.shortcuts import render,redirect
from metronus_app.forms.timeLogForm import TimeLogForm
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

def create(request,task_id):
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
                return redirect('task_list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TimeLogForm(projectDepartment=task.projectDepartment_id, task_id=task_id)


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
    # TODO

    tareas=Task.objects.all()
    month = [x for x in range(1,31)]
    return render(request, "timeLog/timeLog_list_all.html", {"tasks": tareas, "month":month})

def edit(request, timeLog_id):
    return "2"  # TODO

def delete(request, timeLog_id):
    return "2"  # TODO

def findTask(task_id):
    task = get_object_or_404(Task,pk=task_id)
    return task

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
    isAdminOrTeamManager = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                                        role_id__name__in=["Administrator",
                                                                                           "Team manager"])
    res = isAdminOrTeamManager.count() > 0
    if not res:
        roles = ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee,
                                                             projectDepartment_id=task.projectDepartment_id,
                                                             role_id__name__in=["Project manager", "Department manager",
                                                                                "Coordinator"])
        res = roles.count() > 0
    return res
