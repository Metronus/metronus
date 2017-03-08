from metronus_app.model.employee                      import Employee
from metronus_app.model.company                       import Company
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

from django.core.exceptions                           import PermissionDenied
from django.shortcuts                                 import render_to_response
 
from metronus_app.common_utils                        import get_current_admin_or_403


def manage(request):
    """
    parameters/returns:
    departments: lista de los departamentos de la empresa del administrador logueado
    projects: lista de los proyectos de la empresa del administrador logueado
    
    template:
    manage_roles.html
    """

    admin = get_current_admin_or_403(request)
    company = admin.company_id

    # Return all departments and roles for the logged admin
    if request.method == "GET":
        projects = Project.objects.filter(company_id=company)
        departments = Department.objects.filter(company_id=company)
        return render_to_response('manage_roles.html', {'departments': departments, 'projects': projects})
    elif request.method == "POST":
        process_post_roles(request)
    else:
        raise PermissionDenied

########################################################################################################################################
########################################################################################################################################
########################################################################################################################################

def process_post_roles(request):
    pass #TODO