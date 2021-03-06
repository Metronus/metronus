from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField, Q
from django.core import serializers

from metronus_app.forms.taskForm import TaskForm
from metronus_app.model.task import Task
from metronus_app.model.project import Project
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.employee import Employee
from metronus_app.model.department import Department
from metronus_app.model.goalEvolution import GoalEvolution
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.common_utils import default_round,get_actor_or_403,same_company_or_403,is_executive, get_highest_role_tier


from datetime import date, timedelta, datetime

import re


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
    actor = check_task(request,None)
    errors = []

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:

        if form.is_valid():
            # process the data in form.cleaned_data as required
            errors=process_task_form(form)

            pname = form.cleaned_data['name']
            ppro = form.cleaned_data['project_id']
            pdep = form.cleaned_data['department_id']
            pdtuple = find_tuple(ppro, pdep, actor)
            if ppro.deleted:
                errors.append('task_creation_project_inactive')
            if not pdep.active:
                errors.append('task_creation_department_inactive')
            if pdtuple is None:
                errors.append('task_creation_project_department_not_related')
            else:
                pro = find_name(pname,pdtuple)
                if pro is not None:
                    errors.append('task_creation_repeated_name')

            if not errors:
                tid = create_task(form, pdtuple, actor)
                return HttpResponseRedirect('/task/view/{0}/' .format( tid))
            else:
                errors.append('task_creation_error')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaskForm()
    coll = find_collections(request)
    return render(request, 'task/task_form.html', {'form': form, 'errors': errors,
                                              "departments": coll["departments"], "projects": coll["projects"]})


def create_async(request):
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
    actor = check_task(request,None)

    errors = []
    data = {
        'success': True
    }
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:

        if form.is_valid():
            # process the data in form.cleaned_data as required
            errors=process_task_form(form)

            pname = form.cleaned_data['name']
            ppro = form.cleaned_data['project_id']
            pdep = form.cleaned_data['department_id']

            pdtuple = find_tuple(ppro, pdep, actor)
            if ppro.deleted:
                errors.append('task_creation_project_inactive')
            if not pdep.active:
                errors.append('task_creation_department_inactive')
            if pdtuple is None:
                errors.append('task_creation_project_department_not_related')
            else:
                pro = find_name(pname, pdtuple)
                if pro is not None:
                    errors.append('task_creation_repeated_name')

            if not errors:
                create_task(form, pdtuple, actor)
                return JsonResponse(data)
        else:
            errors.append('task_creation_error')
    # if a GET (or any other method) we'll create a blank form
    else:
        return HttpResponseRedirect('/department/create')
    data['success'] = False
    data['errors'] = errors

    return JsonResponse(data)



def form_departments(request):
    """
    parameters:
    project_id: el proyecto asociado
    returns:
    departments :la lista de departamentos
    """
    response = serializers.serialize("json", find_departments(request))
    return HttpResponse(response, content_type='application/json')


def list_tasks(request):
    """
    returns:
    tasks: lista de tareas del actor logeado

    template:
    task_list.html
    """
    # Check that the user is logged in
    tasks = get_list_for_role(request)
    active = tasks.filter(active=True)
    inactive = tasks.filter(active=False)
    return render(request, "task/task_list.html",
            {"tasks": active, "inactive":inactive})

def list_tasks_search(request,name):
    """
    returns:
    tasks: lista de tareas del actor logeado

    template:
    task_list.html
    """

    # Check that the current user has permissions
    tasks = get_list_for_role(request).filter(active=True)

    if name != "all_true":
        tasks = tasks.filter(name__icontains=name)

    return render(request, "task/task_search.html",
        {"tasks": tasks})

def view(request, task_id):
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
    actor=check_task(request,task, for_view=True)
    same_company_or_403(actor,task.actor_id)

    goal_evolution = GoalEvolution.objects.filter(task_id=task.id)
    #employees = Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__task=task.id,
    #    projectdepartmentemployeerole__role_id__tier__lte=20).distinct()
    employees = Employee.objects.filter(timelog__task_id=task.id).distinct()
    return render(request, "task/task_view.html", {"task": task, "goal_evolution": goal_evolution, "employees": employees})


def edit(request, task_id):
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
    task = get_object_or_404(Task, pk=task_id)
    actor=check_task(request,task)
    same_company_or_403(actor,task.actor_id)

    errors = []

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaskForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            errors=process_task_form(form)
            # find tasks with the same name
            pro = Task.objects.filter(name=form.cleaned_data['name'],
                                      projectDepartment_id=task.projectDepartment_id).first()

            # pro does not exists or it's the same
            if pro is not None and pro.id != task.id:
                errors.append('task_creation_repeated_name')

            if not errors:
                update_task(task, form, actor)
                return HttpResponseRedirect('/task/list')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaskForm(initial={"name": task.name, "description": task.description,
                                 "task_id": task.id,
                                 "production_goal": task.production_goal if task.production_goal is not None else "",
                                 "goal_description": task.goal_description if task.goal_description is not None else "",
                                 "project_id": task.projectDepartment_id.project_id,
                                 "department_id": task.projectDepartment_id.department_id,
                                 "price_per_unit": task.price_per_unit if task.price_per_unit is not None else "",
                                 "price_per_hour": task.price_per_hour if task.price_per_hour is not None else ""})
    # The project

    return render(request, 'task/task_form.html', {'form': form, "errors": errors,
                                              "departments": [task.projectDepartment_id.department_id], "projects": [task.projectDepartment_id.project_id]})


def delete(request, task_id):
    """
    parameters:
    task_id: the task id to delete

    returns:
    nothing

    template:
    task_list.html
    """
    # Check that the user is logged in
    task = get_object_or_404(Task, pk=task_id, active=True)
    actor=check_task(request,task)
    same_company_or_403(actor,task.actor_id)

    delete_task(task)

    return HttpResponseRedirect('/task/list')

def recover(request, task_id):
    """
    parameters:
    task_id: the task id to recover

    returns:
    nothing

    template:
    task_list.html
    """
    # Check that the user is logged in
    task = get_object_or_404(Task, pk=task_id, active=False)
    actor=check_task(request,task)
    same_company_or_403(actor,task.actor_id)

    recover_task(task)

    return HttpResponseRedirect('/task/list')


# Métodos para métricas
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

    actor=get_actor_or_403(request)

    if "task_id" not in request.GET:
        raise SuspiciousOperation

    task_id = request.GET["task_id"]
    task=get_object_or_404(Task, pk=task_id)
    actor=check_task(request,task,for_view=True)
    same_company_or_403(actor,task.actor_id)

    # Get and parse the dates and the offset
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

    # --------------------------------------------------------------------------
    dates = []
    str_dates = []

    d1 = datetime.strptime(start_date[0:19] + start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19] + end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1  # timedelta

    for i in range(delta.days + 1):
        str_dates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))

    data = {"days": str_dates, "production": [], "goal_evolution": []}
    index = 0
    # Save productivity for each  date
    # for each date, we will find the asociated timelog
    for log_date in dates:
        log = TimeLog.objects.filter(task_id=task_id, workDate__year=log_date.year, workDate__month=log_date.month,
                                     workDate__day=log_date.day).aggregate(
            total_duration=Sum(  F("duration")/60.0, output_field=FloatField()),
            total_produced_units=Sum(  F("produced_units"), output_field=FloatField()))
        if log is None:
            # Not work that day
            total_productivity = 0
            total_duration = 0
        else:
            total_produced_units = log["total_produced_units"]
            total_duration = log["total_duration"]
            if total_duration == 0 or total_duration is None:
                total_productivity = 0
            else:
                # If not produced but spent time, 0 productivity (you lazy guy...)
                if total_produced_units is None:
                    total_productivity = 0
                else:
                    total_productivity = total_produced_units/total_duration

        # Find the registry date of production goal evolution which is closest to the date
        expected_productivity = GoalEvolution.objects.filter(task_id_id=task_id,
                                                             registryDate__gte=log_date).first()

        # If we do not find the goal or if the date is after the last task update, it may be the current task goal
        if total_duration==0 or total_duration is None:
            expected_productivity=0
        else:
            if expected_productivity is None or task.registryDate <= log_date:
                expected_productivity = task.production_goal
            else:
                expected_productivity = expected_productivity.production_goal

        data["production"].append(default_round(total_productivity))
        data["goal_evolution"].append(default_round(expected_productivity))


    return JsonResponse(data)


def ajax_profit_per_date(request, task_id):
    """
    # url = task/ajax_profit_per_date/<task_id>
    # Devuelve un objeto con las fechas y las rentabilidades diarias y acumuladas
    #

    # Parámetro obligatorio:
    # task_id - ID de la tarea

    # Parámetros opcionales:
    # start_date - fecha en formato YYYY-MM-DD que indica el inicio de la medición. Por defecto, 30 días antes de la fecha actual.
    # end_date - fecha en formato YYYY-MM-DD que indica el final de la medición. Por defecto, fecha actual.
    # offset - desplazamiento (huso) horario en formato +/-HH:MM - Por defecto +00:00

    # Si se proporcionan pero no tienen el formato correcto se lanzará un error HTTP 400 Bad Request

    #devuelve lo siguiente
    #{"acumExpenses": [0, 1457.18015695298, 3071.32603956358, 4438.9463044226895, 6465.819587171869, 7912.658013249849, 9791.46399488711, 11615.32872003681, 13494.726436052111, 15102.72092592163, 16718.442225021892, 18327.93613617256, 20841.87940297534, 22953.949544558982, 24314.625169466122, 25683.231076691303, 27287.16055422502, 28760.84364198999, 31104.25163724206, 32808.89759982555, 34747.27999087272, 36150.9847742294, 37523.6098087571, 38600.05927001698, 40953.76583717958, 42469.88703139726, 44081.49130458021, 45420.3135021882, 47945.57927018715, 49368.262834629466, 51133.932803674485],
    "acumIncome": [0, 155861.848663544, 262457.90948135697, 396454.85575838294, 572637.4741922909, 703418.0032829699, 889130.2419483919, 1057821.248373874, 1259349.275922576, 1393310.956579081, 1539441.608896949, 1700420.3827038072, 1955067.034572835, 2187486.6539142523, 2300530.309442004, 2429378.038836404, 2615789.2939997134, 2742614.2371285204, 3004214.3219032744, 3205025.4834073624, 3363963.7766520614, 3552325.908039063, 3718850.184141958, 3833661.86021891, 4044009.6991582112, 4159278.365569177, 4285423.634163346, 4417334.086840815, 4692230.750316469, 4819759.243153938, 4997733.5628708275],
    "dates": ["2017-03-21", "2017-03-22", "2017-03-23", "2017-03-24", "2017-03-25", "2017-03-26", "2017-03-27", "2017-03-28", "2017-03-29", "2017-03-30", "2017-03-31", "2017-04-01", "2017-04-02", "2017-04-03", "2017-04-04", "2017-04-05", "2017-04-06", "2017-04-07", "2017-04-08", "2017-04-09", "2017-04-10", "2017-04-11", "2017-04-12", "2017-04-13", "2017-04-14", "2017-04-15", "2017-04-16", "2017-04-17", "2017-04-18", "2017-04-19", "2017-04-20"],
    "income": [0, 155861.848663544, 106596.060817813, 133996.946277026, 176182.618433908, 130780.529090679, 185712.238665422, 168691.006425482, 201528.027548702, 133961.680656505, 146130.652317868, 160978.773806858, 254646.651869028, 232419.619341417, 113043.655527752, 128847.7293944, 186411.255163309, 126824.943128807, 261600.084774754, 200811.161504088, 158938.293244699, 188362.131387002, 166524.276102895, 114811.676076952, 210347.838939301, 115268.666410966, 126145.268594169, 131910.452677469, 274896.663475654, 127528.492837469, 177974.319716889],
    "expenses": [0, 1457.18015695298, 1614.1458826106, 1367.62026485911, 2026.87328274918, 1446.83842607798, 1878.80598163726, 1823.8647251497, 1879.3977160153, 1607.99448986952, 1615.72129910026, 1609.49391115067, 2513.94326680278, 2112.07014158364, 1360.67562490714, 1368.60590722518, 1603.92947753372, 1473.68308776497, 2343.40799525207, 1704.64596258349, 1938.38239104717, 1403.70478335668, 1372.6250345277, 1076.44946125988, 2353.7065671626, 1516.12119421768, 1611.60427318295, 1338.82219760799, 2525.26576799895, 1422.68356444232, 1765.66996904502]}  "expected_productivity": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 4.0, 4.0, 2.0, 2.0, 2.0]}}
    """
    task=get_object_or_404(Task, pk=task_id)
    actor=check_task(request,task,for_view=True)
    same_company_or_403(actor,task.actor_id)

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

    # Get all dates between start and end
    dates = []
    str_dates = []

    d1 = datetime.strptime(start_date[0:19] + start_date[20:22], '%Y-%m-%d %H:%M%z')
    d2 = datetime.strptime(end_date[0:19] + end_date[20:22], '%Y-%m-%d %H:%M%z')
    delta = d2 - d1  # timedelta

    for i in range(delta.days + 1):
        str_dates.append((d1 + timedelta(days=i)).date().strftime("%Y-%m-%d"))
        dates.append(d1 + timedelta(days=i))

    data = {'dates': str_dates, 'expenses': [], 'income': [], 'acumExpenses': [], 'acumIncome': []}

    # Profit
    # for each date, we will find all logs, calculate the sum and acumulate it
    index = 0
    for log_date in dates:
        logs = TimeLog.objects.filter(task_id__id=task_id,
                                      workDate__year=log_date.year, workDate__month=log_date.month,
                                      workDate__day=log_date.day).distinct()
        expenses = logs.aggregate(
            total_expenses=Sum(F("duration") / 60.0 * F("employee_id__price_per_hour"), output_field=FloatField()))["total_expenses"]
        expenses = expenses if expenses is not None else 0
        income = logs.aggregate(total_income=Sum(F("task_id__price_per_unit") * F("produced_units"))
                                )["total_income"]
        income = income if income is not None else 0

        data['expenses'].append(default_round(expenses))
        data['income'].append(default_round(income))
        if index == 0:
            data['acumExpenses'].append(default_round(expenses))
            data['acumIncome'].append(default_round(income))
        else:
            data['acumExpenses'].append(default_round(data['acumExpenses'][index - 1] + expenses))
            data['acumIncome'].append(default_round(data['acumIncome'][index - 1] + income))
        index += 1

    return JsonResponse(data)


# #########################################################################################################################################
# Auxiliar methods, containing the operation logic
# #########################################################################################################################################
def process_task_form(form):
    """
    adds errors if exists and returns a list with then
    """
    errors=[]
    if not check_goal(form):
        errors.append('task_creation_invalid_goal')
    if not check_price(form):
        errors.append('task_creation_invalid_price')

    return errors
def create_task(form, project_department, actor):
    """Creates a task supposing the data in the form is ok"""
    fname = form.cleaned_data['name']
    fdescription = form.cleaned_data['description']
    fgoal = form.cleaned_data['production_goal']
    fgoaldescription = form.cleaned_data['goal_description']
    fperunit = form.cleaned_data['price_per_unit']
    fperhour = form.cleaned_data['price_per_hour']

    created_task = Task.objects.create(name=fname, description=fdescription,
                        projectDepartment_id=project_department, actor_id=actor,
                        production_goal=fgoal, goal_description=fgoaldescription,
                        price_per_unit=fperunit, price_per_hour=fperhour)

    return created_task.id


def update_task(task, form, actor):
    """Updates a task and saves the data in the log"""
    new_goal_entry(task, form, actor)
    task.name = form.cleaned_data['name']
    task.description = form.cleaned_data['description']
    task.production_goal = form.cleaned_data['production_goal']
    task.goal_description = form.cleaned_data['goal_description']
    task.price_per_unit = form.cleaned_data['price_per_unit']
    task.price_per_hour = form.cleaned_data['price_per_hour']
    task.save()


def new_goal_entry(task, form, actor):
    """
    Creates a new entry in the goal production if the parameters were checked
    """
    fgoal = form.cleaned_data['production_goal']
    fgoaldescription = form.cleaned_data['goal_description']
    fperunit = form.cleaned_data['price_per_unit']
    fperhour = form.cleaned_data['price_per_hour']
    if fgoal != task.production_goal or fgoaldescription != task.goal_description or fperhour != task.price_per_hour or fperunit != task.price_per_unit:
        GoalEvolution.objects.create(task_id=task,
                                     actor_id=actor,
                                     production_goal=task.production_goal,
                                     goal_description=task.goal_description,
                                     price_per_unit=task.price_per_unit,
                                     price_per_hour=task.price_per_hour)


def check_goal(form):
    """
    This returns true if both goal and description are empty or both are not empty
    """
    fgoal = form.cleaned_data['production_goal']
    fgoaldescription = form.cleaned_data['goal_description']
    return (fgoal != "" and fgoaldescription != "" and fgoal is not None and fgoaldescription is not None) or (not fgoal and not fgoaldescription)


def check_price(form):
    """
    This returns true if the price field is valid
    This means only per_unit or per_hour must be filled
    and only if there is a valid goal description for the first field, or no goal for the second
    """
    fgoaldescription = form.cleaned_data['goal_description']
    fperunit = form.cleaned_data['price_per_unit']
    fperhour = form.cleaned_data['price_per_hour']
    return (fgoaldescription is not None and fgoaldescription != "" and fperhour is None and fperunit is not None and fperunit > 0) or \
        ((fgoaldescription is None or fgoaldescription == "") and fperunit is None and fperhour is not None and fperhour > 0)


def delete_task(task):
    """Deletes a task"""
    task.active = False
    task.save()

def recover_task(task):
    """Recovers a task"""
    task.active = True
    task.save()

def get_list_for_role(request):
    """
    Gets the list of tasks according to the role tier of the logged user
    """
    actor=get_actor_or_403(request)
    highest=get_highest_role_tier(actor)

    if highest < 20:
        raise PermissionDenied
    elif highest>=50:
        return Task.objects.filter(actor_id__company_id=actor.company_id).distinct().order_by("name")
    else:
        return Task.objects.filter(actor_id__company_id=actor.company_id,
            projectDepartment_id__project_id__deleted=False,
            projectDepartment_id__department_id__active=True,
            projectDepartment_id__projectdepartmentemployeerole__role_id__tier__gte=20,
            projectDepartment_id__projectdepartmentemployeerole__employee_id=actor).distinct()


def find_name(pname, project_department):
    """
    Returns whether there is already a task with the tuple project-department
    """
    return Task.objects.filter(name=pname, projectDepartment_id=project_department).first()


def find_tuple(project, department, actor):
    """
    Returns a tuple project-department
    """
    same_company_or_403(actor,project)
    same_company_or_403(actor,department)

    return ProjectDepartment.objects.filter(project_id=project, department_id=department).first()


def find_collections(request):
    """
    Gets the projects and departments the logged user can create tasks for, depending to their roles
    """
    actor=get_actor_or_403(request)
    if actor.user_type == "A" or is_executive(actor):
        proyectos = Project.objects.filter(company_id=actor.company_id, deleted=False)
        departamentos = Department.objects.filter(company_id=actor.company_id, active=True)
    else:
        # not an executive

        roles_dep = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor, role_id__tier__gte=20)

        if roles_dep.count() > 0:
            # you're a project manager. Loading your projects
            proyectos = Project.objects.filter(
                company_id=actor.company_id, deleted=False,
                projectdepartment__projectdepartmentemployeerole__employee_id=actor)
            departamentos = Department.objects.filter(
                company_id=actor.company_id, active=True,
                projectdepartment__projectdepartmentemployeerole__employee_id=actor)
        else:
            # not any of this? get outta here!!
            raise PermissionDenied

    return {"departments": departamentos.distinct(), "projects": proyectos.distinct()}


def find_departments(request):
    """
    Gets the  departments the logged user can create tasks for a project, depending to their roles
    """
    if "project_id" not in request.GET:
        raise SuspiciousOperation

    project_id = request.GET.get("project_id")

    actor=get_actor_or_403(request)
    if actor.user_type == "A" or is_executive(actor):
        departamentos = Department.objects.filter(projectdepartment__project_id_id=project_id,company_id=actor.company_id, active=True)
    else:

        # not an executive
        roles_dep = ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor, role_id__tier__gte=20,
            projectDepartment_id__project_id__deleted=False,projectDepartment_id__department_id__active=True)

        if roles_dep.count() > 0:
            # you're a project manager or a coordinator. Loading your departments for the selected project
            departamentos = Department.objects.filter(
                company_id=actor.company_id, active=True,
                projectdepartment__projectdepartmentemployeerole__employee_id=actor,
                projectdepartment__project_id_id=project_id)
        else:
            # not any of this? get outta here!!
            raise PermissionDenied
    return departamentos.distinct()


def check_task(request,task, for_view=False):
    """
    checks if the task belongs to the logged actor with appropiate roles
    """
    actor=get_actor_or_403(request)
    highest=get_highest_role_tier(actor)

    if highest>=50:
        # Admins and executives can do everything
        return actor
    elif task:
        if not task.active:
            raise PermissionDenied
        # If it's for view, project managers can see tasks in their projects but not their departments
        elif for_view and highest>=20: 
            if highest >= 40 and ProjectDepartmentEmployeeRole.objects.filter(
                Q(employee_id=actor),
                Q(role_id__tier__gte=40),
                (Q(projectDepartment_id__department_id=task.projectDepartment_id.department_id) | Q(projectDepartment_id__project_id=task.projectDepartment_id.project_id))) \
                    .exists():
                return actor
            elif ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
                projectDepartment_id=task.projectDepartment_id,
                role_id__tier__gte=20).exists():
                return actor
        elif ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor,
            projectDepartment_id=task.projectDepartment_id,
            role_id__tier__gte=20).exists():
            # If it's for view, coordinators and greater can access too
            return actor
    elif highest>=20:
        # If it's for creation, task is None
        return actor

    # Otherwise GTFO
    raise PermissionDenied
