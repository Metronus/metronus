from django import template
from datetime import datetime
import calendar
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

register = template.Library()


def get_type(ob):
    return ob.field.widget.__class__.__name__


def get_form_type(form_type):
    return {
        'TextInput': 'text',
        'PasswordInput': 'password',
        'EmailInput': 'email',
        'ClearableFileInput': 'file'
    }.get(form_type, 'text')


@register.inclusion_tag('tags/form.html')
def show_form(form):
    return {'form': form}


@register.inclusion_tag('tags/field.html')
def show_field(field, required=True):
    return {'field': field, 'required': "required" if required else "", 'type': get_form_type(get_type(field))}

@register.inclusion_tag('tags/team_item.html')
def team_item(name, img_name, role):
    return {'name': name,'img_name': img_name,'role' : role}

@register.inclusion_tag('tags/ajaxErrors.html')
def show_ajax_errors():
    return {}


@register.simple_tag
def converto_to_hours(amount):
    """ ¿converto o con berto? XD"""
    hours = amount//60
    minutes = amount % 60
    if minutes < 10:
        minutos = "0"+str(minutes)
    else:
        minutos = str(minutes)
    return str(hours)+":"+minutos if amount != 0 else ""


@register.simple_tag
def is_weekend(day, month, year):
    result = True
    if day != "Total" and int(day) != calendar.monthrange(year, month)[1]+1:
        fecha = datetime(year, month, day).date()
        result = fecha.weekday() in (5, 6)
    return "success" if result else ""


@register.assignment_tag
def is_admin(actor):
    return actor.user_type == 'A'


@register.assignment_tag
def has_role(actor):
    if actor.user_type == 'E' or actor.user_type == 'A':
        try:
            return ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor.id).count() > 0
        except:
            return False
    else:
        return False


@register.assignment_tag
def is_employee(actor):
    if actor.user_type == 'A' or not has_role(actor):
        return False

    for role in ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor.id):
        if role.role_id.name == 'EMPLOYEE':
            return True

    return False


@register.assignment_tag
def is_project_manager(actor):
    if actor.user_type == 'A' or not has_role(actor):
        return False

    for role in ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor.id):
        if role.role_id.name == 'PROJECT_MANAGER':
            return True

    return False


@register.assignment_tag
def is_coordinator(actor):
    if actor.user_type == 'A' or not has_role(actor):
        return False

    for role in ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor.id):
        if role.role_id.name == 'COORDINATOR':
            return True

    return False


@register.assignment_tag
def is_executive(actor):
    if actor.user_type == 'A' or not has_role(actor):
        return False

    for role in ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor.id):
        if role.role_id.name == 'EXECUTIVE':
            return True

    return False


@register.assignment_tag
def is_team_manager(actor):
    if actor.user_type == 'A' or not has_role(actor):
        return False

    for role in ProjectDepartmentEmployeeRole.objects.filter(employee_id=actor.id):
        if role.role_id.name == 'TEAM_MANAGER':
            return True

    return False
