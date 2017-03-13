from metronus_app.model.employee                      import Employee
from metronus_app.model.role                          import Role
from metronus_app.model.company                       import Company
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.projectDepartment             import ProjectDepartment
from metronus_app.forms.roleManagementForm            import RoleManagementForm

from django.core.exceptions                           import PermissionDenied, ObjectDoesNotExist
from django.shortcuts                                 import render_to_response, get_object_or_404
from django.http                                      import HttpResponseBadRequest 
 
from metronus_app.common_utils                        import get_current_admin_or_403


def manage(request):
    """
    parameters/returns:

    employee_id: id del empleado (si el formulario es nuevo)
    role_id: id del rol a editar (si se edita uno ya existente)

    returns:
    departments: lista de departamentos de la empresa del admin logueado
    projects: lista de proyectos de la empresa del admin logueado
    roles: lista de roles del sistema
    form: formulario RoleManagementForm con los valores iniciales adecuados
    
    template:
    rol_form.html
    """

    admin = get_current_admin_or_403(request)

    # Return all departments and roles for the logged admin
    if request.method == "GET":
        # Check that the GET request contains at least employee_id or role_id as parameters
        if "employee_id" not in request.GET and "role_id" not in request.GET:
            return HttpResponseBadRequest()

        return return_get_form(request, admin)

    elif request.method == "POST":

        # Process the received form
        
        form = RoleManagementForm(request.POST)
        if form.is_valid():
            check_form_permissions(form, admin)

            if form.cleaned_data['role_id'] == 0:
                # ID = 0, crear un nuevo rol
                create_new_role(form)
            else:
                existing_role = get_object_or_404(ProjectDepartmentEmployeeRole, id=form.cleaned_data['employeeRole_id'])
                if existing_role.employee_id.id != form.cleaned_data['employee_id'] or existing_role.projectDepartment_id.project_id.id != form.cleaned_data['project_id'] or existing_role.projectDepartment_id.department_id.id != form.cleaned_data['department_id']:

                    create_new_role(form) # Treat it like a new role if the employee, the project or the department have changed from the original

                else:
                    # Update the current role
                    existing_role.role_id = get_object_or_404(Role, id=form.cleaned_data['role_id'])
                    existing_role.save()


            return HttpResponseRedirect('/employee/view/' + existing_role.employee_id.user.username + '/')
    else:
        raise PermissionDenied


########################################################################################################################################
########################################################################################################################################
########################################################################################################################################

def create_new_role(form):
    # Permissions are already checked
    dpmt_id = form.cleaned_data['department_id']
    project_id = form.cleaned_data['project_id']
    employee_id = form.cleaned_data['employee_id']
    role_id = form.cleaned_data['role_id']

    # Check if there is an existing role for that combination and overwrites if so
    try:
        existing = ProjectDepartmentEmployeeRole.objects.get(employee_id__id=employee_id, projectDepartment_id__project_id__id=project_id, projectDepartment_id__department_id__id=department_id)
        existing.role_id = get_object_or_404(Role, id=role_id)
        existing.save()
    except ObjectDoesNotExist:
        try:
            pd = ProjectDepartment.objects.find(department_id__id=department_id, project_id__id=project_id)
        except ObjectDoesNotExist:
            pd = ProjectDepartment.objects.create(department_id=department_id, project_id=project_id)
            ProjectDepartmentEmployeeRole.objects.create(projectDepartment_id=pd, employee_id=employee_id, role_id=role_id)


def return_get_form(request, admin):
    company = admin.company_id

    departments = Department.objects.filter(company_id=company)
    projects = Project.objects.filter(company_id=company)
    roles = Role.objects.all()

    if "employee_id" in request.GET:
        # New form
        employee = get_object_or_404(Employee, id=request.GET['employee_id'])
        if employee.company_id != company:
            raise PermissionDenied

        form = RoleManagementForm(initial = {'employee_id': employee.id, 'employeeRole_id': 0})
    else:
        # Edit existing role
        role = get_object_or_404(ProjectDepartmentEmployeeRole, id=request.GET['role_id'])
        
        # Check that the role belongs to the current admin's company
        if role.employee_id.company_id != admin.company_id:
            raise PermissionDenied

        form = RoleManagementForm(initial = {
            'employee_id': role.employee_id.id,
            'department_id': role.projectDepartment_id.department_id.id,
            'project_id': role.projectDepartment_id.project_id.id,
            'role_id': role.role_id.id,
            'employeeRole_id': role.id,
        })

    return render_to_response('rol_form.html', {'departments': departments, 'projects': projects, 'roles': roles, 'form': form})

def check_form_permissions(form, admin):

    employee = get_object_or_404(Employee, id=form.cleaned_data['employee_id'])
    if employee.company_id != admin.company_id:
        raise PermissionDenied

    project = get_object_or_404(Project, id=form.cleaned_data['project_id'])
    if project.company_id != admin.company_id:
        raise PermissionDenied

    dpmt = get_object_or_404(Department, id=form.cleaned_data['department_id'])
    if dpmt.company_id != admin.company_id:
        raise PermissionDenied

    get_object_or_404(Role, id=form.cleaned_data['role_id'])