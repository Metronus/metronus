from django import template
from datetime import datetime
import calendar
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole

register = template.Library()

def get_type(ob):
    return ob.field.widget.__class__.__name__

def get_form_type(type):
    return {
        'TextInput' : 'text',
        'PasswordInput' : 'password',
        'EmailInput' : 'email',
        'ClearableFileInput': 'file'
    }.get(type, 'text')

@register.inclusion_tag('tags/form.html')
def show_form(form):
    return {'form':form}

@register.inclusion_tag('tags/field.html')
def show_field(field, required = True):
    print(get_form_type(get_type(field)))
    return {'field':field, 'required': "required" if required  else "", 'type':get_form_type(get_type(field))}
@register.inclusion_tag('tags/ajaxErrors.html')
def show_ajax_errors():
    return {}
@register.simple_tag
def converto_to_hours(amount):
    hours = amount//60
    minutes = amount%60
    minutos = ""
    if(minutes<10):
        minutos = "0"+str(minutes)
    else:
        minutos = str(minutes)
    return str(hours)+":"+minutos if amount !=0 else ""

@register.simple_tag
def is_weekend(day,month,year):
    result = True
    if day != "Total" and int(day) != calendar.monthrange(year,month)[1]+1:
        fecha = datetime(year,month,day).date()
        result = fecha.weekday() in (5,6)
    return "success" if result else ""

@register.assignment_tag
def isAdmin(actor):
    if actor.user_type == 'A':
        return True
    else:
        return False

@register.assignment_tag
def hasRole(actor):
    if actor.user_type == 'E' or actor.user_type == 'A':
        try:
            role_id = ProjectDepartmentEmployeeRole.objects.get(employee_id = actor.id).role_id
            return True
        except:
            return False
    else:
        return False


@register.assignment_tag
def isEmployee(actor):
    if actor.user_type == 'A' or not hasRole(actor):
        return False

    role_id = ProjectDepartmentEmployeeRole.objects.get(employee_id = actor.id).role_id
    if role_id.name == 'EMPLOYEE':
        return True
    else:
        return False

@register.assignment_tag
def isProjectManager(actor):
    if actor.user_type == 'A' or not hasRole(actor):
        return False

    role_id = ProjectDepartmentEmployeeRole.objects.get(employee_id = actor.id).role_id
    print(role_id.name)
    if role_id.name == 'PROJECT_MANAGER':
        return True
    else:
        return False

@register.assignment_tag
def isCoordinator(actor):
    if actor.user_type == 'A' or not hasRole(actor):
        return False

    role_id = ProjectDepartmentEmployeeRole.objects.get(employee_id = actor.id).role_id
    if role_id.name == 'COORDINATOR':
        return True
    else:
        return False

@register.assignment_tag
def isExecutive(actor):
    if actor.user_type == 'A' or not hasRole(actor):
        return False

    role_id = ProjectDepartmentEmployeeRole.objects.get(employee_id = actor.id).role_id
    if role_id.name == 'EXECUTIVE':
        return True
    else:
        return False

@register.assignment_tag
def isTeamManager(actor):
    if actor.user_type == 'A' or not hasRole(actor):
        return False

    role_id = ProjectDepartmentEmployeeRole.objects.get(employee_id = actor.id).role_id
    if role_id.name == 'TEAM_MANAGER':
        return True
    else:
        return False