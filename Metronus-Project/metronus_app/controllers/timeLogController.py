from django.shortcuts import render
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

def create(request, task_id):
    return "2" #TODO

def list(request, task_id):
    return "2" # TODO

def list_all(request):
    # TODO

    tareas=[t for t in range(1,5)]
    month = [x for x in range(1,31)]
    return render(request, "timeLog_list_all.html", {"tasks": tareas, "month":month})

def edit(request, timeLog_id):
    return "2"  # TODO

def delete(request, timeLog_id):
    return "2"  # TODO
