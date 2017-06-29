from metronus_app.common_utils import get_admin_executive_or_403
from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import render
from django.core.exceptions import SuspiciousOperation

from metronus_app.model.project import Project
from metronus_app.model.employee import Employee
from metronus_app.model.task import Task
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.department import Department

from datetime import date, timedelta
import re


def view(request):
    """
    Standard view for dashboard, is empty as all data will be requested through AJAX
    """
    get_admin_executive_or_403(request)

    return render(request, 'dashboard.html')


def ajax_time_per_project(request):
    """ Devuelve un objeto cuyas claves son las ID de los proyectos y sus valores un objeto {'name': ..., 'time': X} (X en minutos)

    # Parámetros opcionales:
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request
    """
    logged = get_admin_executive_or_403(request)

    # Get and parse the dates
    start_date = request.GET.get("start_date", str(date.today() - timedelta(days=30)))
    end_date = request.GET.get("end_date", str(date.today()))
    date_regex = re.compile("^\d{4}-\d{2}-\d{2}$")

    if date_regex.match(start_date) is None or date_regex.match(end_date) is None:
        raise SuspiciousOperation("Start/end date are not valid")

    offset = request.GET.get("offset", "+00:00")
    offset_regex = re.compile("^(\+|-)\d{2}:\d{2}$")

    if offset_regex.match(offset) is None:
        raise SuspiciousOperation("Time offset is not valid")

    # Append time offsets
    start_date += " 00:00" + offset
    end_date += " 00:00" + offset

    
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)

    data = {}
    # Sum timelogs for each project
    for project in company_projects:
        time_total = TimeLog.objects.filter(
            task_id__active=True,
            task_id__projectDepartment_id__project_id=project,
            workDate__range=[start_date, end_date]).aggregate(Sum('duration'))["duration__sum"]
        if time_total is None:
            time_total = 0

        data[project.id] = {
                            'name': project.name,
                            'time': time_total
                        }

    return JsonResponse(data)


def ajax_employees_per_project(request):
    """
    Gets the number of employees per project
    """
    
    logged = get_admin_executive_or_403(request)
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)
    data = {}
    for project in company_projects:
        data[project.id] = {
            'name': project.name,
            'employees': list(Employee.objects.filter(
                projectdepartmentemployeerole__projectDepartment_id__project_id=project).values('id', 'identifier', 'user__username', 'registryDate'))
        }
    return JsonResponse(data)


def ajax_departments_per_project(request):
    """
    Gets the number of departments per project
    """
    
    logged = get_admin_executive_or_403(request)
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)
    data = {}
    for project in company_projects:
        data[project.id] = {
            'name': project.name,
            'departments': list(Department.objects.filter(projectdepartment__project_id=project).values('id', 'name'))
        }
    return JsonResponse(data)


def ajax_tasks_per_project(request):
    """
    Gets the number of tasks per project
    """
    
    logged = get_admin_executive_or_403(request)
    company_projects = Project.objects.filter(deleted=False, company_id=logged.company_id)
    data = {}
    for project in company_projects:
        data[project.id] = {
            'name': project.name,
            'tasks': list(Task.objects.filter(
                projectDepartment_id__project_id=project).values('id', 'name', 'description'))
        }
    return JsonResponse(data)
