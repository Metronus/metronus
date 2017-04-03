from metronus_app.common_utils import get_current_admin_or_403,get_current_employee_or_403

from django.core.exceptions                             import ObjectDoesNotExist, PermissionDenied
from django.http                                        import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.contrib.auth                                import authenticate,login
from django.db.models                                   import Sum

from metronus_app.forms.projectForm                     import ProjectForm
from metronus_app.model.project                         import Project,Company
from metronus_app.common_utils                          import get_current_admin_or_403
from metronus_app.model.administrator                   import Administrator
from metronus_app.model.employee                        import Employee
from metronus_app.model.task                            import Task
from metronus_app.model.timeLog                         import TimeLog
from metronus_app.model.department                      import Department
from metronus_app.model.projectDepartmentEmployeeRole   import ProjectDepartmentEmployeeRole
from metronus_app.model.actor                           import Actor
from django.shortcuts                                   import render_to_response, get_object_or_404, render,redirect
from datetime                                           import date, timedelta
from django.core import serializers
from metronus_app.model.projectDepartment             import ProjectDepartment

import re


def ajax_time_per_project(request):
    # Devuelve un objeto cuyas claves son las ID de los proyectos y sus valores un objeto {'name': ..., 'time': X} (X en minutos)

    # Parámetros opcionales: 
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    get_current_admin_or_403(request)
   
    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today()))
    end_date = request.GET.get("end_date", str(date.today() - timedelta(days=30)))
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


    logged = request.user.actor
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)

    data = {}
    #Sum timelogs for each project
    for project in company_projects:
        time_total = TimeLog.objects.filter(task_id__active=True,task_id__projectDepartment_id__project_id=project,
                                                           workDate__range=[start_date, end_date]).aggregate(Sum('duration'))["duration__sum"]
        if time_total is None: 
            time_total = 0

        data[project.id] = {
                            'name': project.name,
                            'time': time_total
                        }

    return JsonResponse(data)

def ajax_employees_per_project(request):
    get_current_admin_or_403(request)
    logged = request.user.actor
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)
    data = {}
    for project in company_projects:
        data[project.id] = {
            'name': project.name,
            'employees': list(Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__project_id = project).values('id','user__username'))
        }
    return JsonResponse(data)

def ajax_departments_per_project(request):
    get_current_admin_or_403(request)
    logged = request.user.actor
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)
    data = {}
    for project in company_projects:
        data[project.id] = {
            'name': project.name,
            'departments': list(Department.objects.filter(projectdepartment__project_id=project).values('id','name'))
        }
    return JsonResponse(data)
