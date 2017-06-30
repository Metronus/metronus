from django.shortcuts import render, get_object_or_404
from metronus_app.forms.projectDepartmentForm import ProjectDepartmentForm
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.project import Project
from metronus_app.model.department import Department

from django.http import HttpResponseRedirect
from metronus_app.common_utils import get_current_admin_or_403,same_company_or_403


def create(request):
    """
    parameters/returns:
    form: el formulario con los datos de la clase ProjectDepartment: project_id, department_id;
    y projectDepartment_id, que será 0 en caso de que estemos creando uno.

    template:
    projectdepartment_create.html
    """
    admin = get_current_admin_or_403(request)
    
    if request.method == 'POST':
        form = ProjectDepartmentForm(data=request.POST, user=admin)

        if form.is_valid():
            create_project_department(form, admin)
            return render(request, 'projectDepartment/projectdepartment_create.html',
                          {'form': ProjectDepartmentForm(user=admin), 'success': True})

    # GET -> Create an empty form
    else:
        form = ProjectDepartmentForm(initial={"project_id": 0,
                                              "department_id": 0,
                                              "projectDepartment_id": 0}, user=admin)

    return render(request, 'projectDepartment/projectdepartment_form.html', {'form': form})


def delete(request):
    """
    parameters:
    Recibe el id del projectDepartment a borrar: projectDepartment_id

    template: projectDepartment_list.html
    """

    admin = get_current_admin_or_403(request)
    project_department_id = request.GET.get("projectDepartment_id")
    project_department = get_object_or_404(ProjectDepartment, id=project_department_id)

    delete_project_department(project_department, admin)

    return HttpResponseRedirect('/projectdepartment/list/')


def list_project_department(request):
    """
    parameters: project_id or department_id, both optional.
    If it receives project_id, it will return all projectDepartments from that project
    If it receives department_id, it will return all projectDepartments form that department
    If it receives none, it will return all projectDeparments from the logged company

    returns:
    projectDepartments: lista de relaciones proyecto-departamento de la compañía logeada, según el parámetro pasado.

    template:
    projectdepartment_list.html
    """

    admin = get_current_admin_or_403(request)
    project_id = request.GET.get('project_id')
    department_id = request.GET.get('department_id')

    if project_id is not None:
        project = get_object_or_404(Project, id=project_id)
        same_company_or_403(admin,project)
        lista = ProjectDepartment.objects.filter(project_id=project)

    elif department_id is not None:
        department = get_object_or_404(Department, id=department_id)
        same_company_or_403(admin,department)
        lista = ProjectDepartment.objects.filter(department_id=department)

    else:
        lista = ProjectDepartment.objects.filter(project_id__company_id=admin.company_id)

    return render(request, "projectDepartment/projectdepartment_list.html", {"projectDepartments": lista})


# Auxiliar methods, containing the operation logic

def create_project_department(form, admin):
    """ Creates a link between a project and a department so that tasks can be created for them"""
    project = form.cleaned_data['project_id']
    department = form.cleaned_data['department_id']

    same_company_or_403(admin,project) 
    same_company_or_403(admin,department)

    return ProjectDepartment.objects.create(project_id=project, department_id=department)


def delete_project_department(project_department, admin):
    """Deletes the relationship between a project and a department"""
    same_company_or_403(admin,project_department.department_id)
    same_company_or_403(admin,project_department.project_id)

    project_department.delete()

