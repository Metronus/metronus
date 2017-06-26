from metronus_app.model.employee import Employee
from metronus_app.model.role import Role
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.forms.roleManagementForm import RoleManagementForm

from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse

from metronus_app.common_utils import get_authorized_or_403


def manage(request):
    """
    parameters:
        employee_id: id del empleado (si el formulario es nuevo)
        role_id: id del rol a editar (si se edita uno ya existente)
        Se devuelve error 403 si no se proporciona al menos uno de los dos

    returns:
        employee: datos del empleado que se está editando
        departments: lista de departamentos que puede usar el usuario/admin logueado
        projects: lista de proyectos que puede user el usuario/admin logueado
        roles: lista de roles del sistema (sólo se aceptarán si están por debajo para el dpto/proyecto)
        form: formulario RoleManagementForm con los valores iniciales adecuados

        errors: array de códigos de error si los hay

    template:
        rol_form.html

    códigos de error (todos empiezan por roleCreation_):
        formNotValid - el formulario enviado no es válido
        employeeDoesNotExist - el empleado indicado no existe en la compañía o no está activo
        departmentDoesNotExist - el departamento indicado no existe en la compañía o no está activo
        projectDoesNotExist - el proyecto indicado no existe en la compañía o no está activo
        roleDoesNotExist - el rol indicado no existe
        employeeRoleDoesNotExist - el ID de rol de empleado indicado no existe
        notAuthorizedProjectDepartment - el usuario no está autorizado para crear roles en ese departamento y proyecto
        notAuthorizedRole - el usuario está autorizado a crear roles pero el que intenta crear es igual o superior al suyo
        alreadyExists - ya existe un rol para ese usuario, departamento y proyecto (sólo aparece al crear roles, no al editar)
        editingHigherRole - el usuario está intentando editar un rol de otro usuario que está por encima de él
    """

    logged = get_authorized_or_403(request)

    if request.method == "GET":
        # Check that at least 'employee_id' or 'role_id' are provided as GET params, raise 400 otherwise
        if "employee_id" not in request.GET and "role_id" not in request.GET:
            return HttpResponseBadRequest()

        # Return the initial form
        return get_form(request, logged)

    elif request.method == "POST":

        form = RoleManagementForm(request.POST)
        if form.is_valid():

            result = process_post_form(logged, form)
            if result["ok"]:
                return HttpResponseRedirect('/employee/view/' + Employee.objects.get(id=form.cleaned_data["employee_id"]).user.username + '/')
            else:
                return return_invalid_form(request, form, logged, result["errors"])

        else:
            # The form is not valid
            return return_invalid_form(request, form, logged, ['roleCreation_formNotValid'])

    else:  # Other request method, not supported
        raise PermissionDenied


def manage_async(request):
    """
    parameters:
    form: el formulario con los datos del departamento

    returns:

    JSON con un mensaje de respuesta. Es un dict que contiene lo siguiente
    success: true si hubo exito, false si no
    errors: array de códigos de error (vacío si success == true)
    """

    logged = get_authorized_or_403(request)

    if request.method == 'POST':

        form = RoleManagementForm(request.POST)
        if form.is_valid():
            result = process_post_form(logged, form)
            return JsonResponse({'success': result["ok"], 'errors': result['errors']})
        else:
            return JsonResponse({'success': False, 'errors': ['roleCreation_formNotValid']})


def ajax_departments_from_projects(request):
    """
    parameters:
    project_id: ID del proyecto seleccionado

    returns:
    lista de objetos {id, nombre} de los departamentos seleccionables
    """

    logged = get_authorized_or_403(request)
    if "project_id" not in request.GET:
        return HttpResponseBadRequest()

    if logged.user_type == "E":
        ids = ProjectDepartmentEmployeeRole.objects.values_list('projectDepartment_id__department_id', flat=True).filter(employee_id=logged, role_id__tier__gt=10, projectDepartment_id__department_id__active=True, projectDepartment_id__project_id__id=request.GET["project_id"])
        dpts = Department.objects.filter(id__in=ids)
    else:
        dpts = Department.objects.filter(active=True, company_id=logged.company_id)

    data = []
    for d in dpts:
        data.append({'id': d.id, 'name': d.name})

    return JsonResponse(data, safe=False)


def ajax_roles_from_tuple(request):
    """
    parameters:
    project_id: ID del proyecto seleccionado
    department_id: ID del proyecto seleccionado

    returns:
    lista de objetos {id, nombre} de los roles seleccionables
    """

    logged = get_authorized_or_403(request)
    if "project_id" not in request.GET or "department_id" not in request.GET:
        return HttpResponseBadRequest()

    if logged.user_type == "E":
        try:
            myrole = ProjectDepartmentEmployeeRole.objects.get(employee_id=logged, projectDepartment_id__project_id__id=request.GET["project_id"], projectDepartment_id__department_id__id=request.GET["department_id"])
            roles = Role.objects.filter(tier__lt=myrole.role_id.tier)
        except:
            raise PermissionDenied
    else:
        roles = Role.objects.all()

    data = []
    for r in roles:
        data.append({'id': r.id, 'name': r.name})

    return JsonResponse(data, safe=False)


def delete(request, role_id):
    """
    url: /roles/delete/<role_id>

    parameters/returns:
    role_id: id del rol a borrar

    returns: redirecciona a la vista del empleado en cuestión o devuelve 404 (si no existe) / 403 (si no está autorizado)

    El botón de borrar sólo se debería mostrar si el usuario en cuestión está autorizado a borrar el rol, por lo que no se devuelven códigos de error.
    """

    logged = get_authorized_or_403(request)
    role = get_object_or_404(ProjectDepartmentEmployeeRole, id=role_id)

    check_companies_match(logged, role.employee_id)

    if logged.user_type == 'E':
        try:
            logged_role = ProjectDepartmentEmployeeRole.objects.get(employee_id=logged,
                                                                    projectDepartment_id=role.projectDepartment_id)
            if role.role_id.tier >= logged_role.role_id.tier:
                raise PermissionDenied

        except ObjectDoesNotExist:
            raise PermissionDenied

    employee_username = role.employee_id.user.username
    role.delete()

    return HttpResponseRedirect('/employee/view/' + employee_username)


###########################################################################################

def process_post_form(logged, form):
    """
    checks the form verifies all logic constraints and generate errors if they are violated
    """
    res = {'errors': [], 'ok': False}

    employee_id = form.cleaned_data["employee_id"]
    department_id = form.cleaned_data["department_id"]
    project_id = form.cleaned_data["project_id"]
    role_id = form.cleaned_data["role_id"]
    employee_role_id = form.cleaned_data["employeeRole_id"]

    company = logged.company_id

    # Check that everything exists and is within the logged user's company
    try:
        employee = Employee.objects.get(id=employee_id, user__is_active=True, company_id=company)
    except ObjectDoesNotExist:
        res["errors"].append('roleCreation_employeeDoesNotExist')

    try:
        department = Department.objects.get(id=department_id, active=True, company_id=company)
    except ObjectDoesNotExist:
        res["errors"].append('roleCreation_departmentDoesNotExist')

    try:
        project = Project.objects.get(id=project_id, deleted=False, company_id=company)
    except ObjectDoesNotExist:
        res["errors"].append('roleCreation_projectDoesNotExist')

    try:
        role = Role.objects.get(id=role_id)
    except ObjectDoesNotExist:
        res["errors"].append('roleCreation_roleDoesNotExist')

    if employee_role_id:  # employeeRole_id != 0
        try:
            employee_role = ProjectDepartmentEmployeeRole.objects.get(id=employee_role_id)
        except ObjectDoesNotExist:
            res["errors"].append('roleCreation_employeeRoleDoesNotExist')

    # Return now if there are errors
    if res["errors"]:
        return res

    if logged.user_type == 'E':  # Admins have all privileges

        # Check that the logged user has a ProjDpmtEmplRole for that tuple
        try:
            logged_role = ProjectDepartmentEmployeeRole.objects.get(employee_id=logged, projectDepartment_id__department_id=department, projectDepartment_id__project_id=project)
        except ObjectDoesNotExist:
            res["errors"].append('roleCreation_notAuthorizedProjectDepartment')

        # Return now if there are errors
        if res["errors"]:
            return res

        # Check that the role that the logged user is trying to assign is below his current role
        if logged_role.role_id.tier <= role.tier:
            res["errors"].append('roleCreation_notAuthorizedRole')

        # Return now if there are errors
        if res["errors"]:
            return res

    if employee_role_id == 0:
        # We are creating a new role, check that it doesn't yet exist
        if ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee, projectDepartment_id__department_id=department, projectDepartment_id__project_id=project).count() > 0:
            res["errors"].append('roleCreation_alreadyExists')
            return res

        # Everything is okay now, create the role
        try:
            pd = ProjectDepartment.objects.get(department_id=department, project_id=project)
        except ObjectDoesNotExist:
            pd = ProjectDepartment.objects.create(department_id=department, project_id=project)

        ProjectDepartmentEmployeeRole.objects.create(projectDepartment_id=pd, employee_id=employee, role_id=role)

    else:
        # We are editing an existing role
        if logged.user_type == 'E' and logged_role.role_id.tier <= employee_role.role_id.tier:
            res["errors"].append('roleCreation_editingHigherRole')
            return res

        employee_role.role_id = role
        employee_role.save()

    res["ok"] = True
    return res


def return_invalid_form(request, form, logged, errors=None):
    employee = get_object_or_404(Employee, id=form.cleaned_data.get('employee_id', 0), user__is_active=True)
    return render(request, 'role/rol_form.html', {'departments': get_allowed_departments(logged),
                                                  'projects': get_allowed_projects(logged),
                                                  'roles': Role.objects.all(),
                                                  'form': form,
                                                  'employee': employee,
                                                  'errors': errors,
                                                  'editing': "employeeRole_id" in form.cleaned_data and form.cleaned_data["employeeRole_id"] != 0})


def get_form(request, logged):
    """
    returns the form and populates with the role data if we are editing, otherwise we are assigning a new role to an employee
    """
    departments = get_allowed_departments(logged)
    projects = get_allowed_projects(logged)
    roles = Role.objects.all()

    if "employee_id" in request.GET:
        employee_id_get = request.GET["employee_id"]

        # Return 404 if no employee with such id exists
        employee = get_object_or_404(Employee, id=employee_id_get, user__is_active=True, company_id=logged.company_id)

        form = RoleManagementForm(initial={'employee_id': employee.id, 'employeeRole_id': 0})

    else:
        # Editing an existing role
        role = get_object_or_404(ProjectDepartmentEmployeeRole, id=request.GET['role_id'])
        employee = role.employee_id

        check_companies_match(employee, logged)

        form = RoleManagementForm(initial={
            'employee_id': employee.id,
            'department_id': role.projectDepartment_id.department_id.id,
            'project_id': role.projectDepartment_id.project_id.id,
            'role_id': role.role_id.id,
            'employeeRole_id': role.id,
        })

    # Pass a boolean parameter to the frontent that indicates whether we are editing o creating a role
    # This was a direct request from the frontend team

    editing = 'role_id' in request.GET

    return render(request, 'role/rol_form.html', {'employee': employee, 'departments': departments,
                                                  'projects': projects, 'roles': roles, 'form': form,
                                                  'editing': editing})


def check_companies_match(act1, act2):
    """Checks the roles from both actors match"""
    if act1.company_id != act2.company_id:
        raise PermissionDenied


def get_allowed_departments(logged):
    """Gets the departments the logged user can create roles for"""
    if logged.user_type == 'A':
        return Department.objects.filter(company_id=logged.company_id, active=True)
    else:
        # Return the departments in which the user has a role higher than Employee
        ids = ProjectDepartmentEmployeeRole.objects.values_list('projectDepartment_id__department_id', flat=True).filter(employee_id=logged, role_id__tier__gt=10, projectDepartment_id__department_id__active=True)
        return Department.objects.filter(id__in=ids)


def get_allowed_projects(logged):
    """Gets the projects the logged user can create roles for"""
    if logged.user_type == 'A':
        return Project.objects.filter(company_id=logged.company_id, deleted=False)
    else:
        # Return the departments in which the user has a role higher than Employee
        ids = ProjectDepartmentEmployeeRole.objects.values_list('projectDepartment_id__project_id', flat=True).filter(employee_id=logged, role_id__tier__gt=10, projectDepartment_id__project_id__deleted=False)
        return Project.objects.filter(id__in=ids)
