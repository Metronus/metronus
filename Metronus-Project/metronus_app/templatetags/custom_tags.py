from django import template
from datetime import datetime
import calendar

register = template.Library()

def get_type(ob):
    return ob.field.widget.__class__.__name__

def get_form_type(type):
    return {
        'TextInput' : 'text',
        'PasswordInput' : 'password',
        'EmailInput' : 'email'
    }.get(type, 'text')

@register.inclusion_tag('tags/form.html')
def show_form(form):
    return {'form':form}

@register.inclusion_tag('tags/field.html')
def show_field(field, required = True):
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
    return actor.user_type == 'A'

@register.assignment_tag
def isEmployee(actor):
    return actor.user_type == 'E'