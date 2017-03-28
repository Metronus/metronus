from django import template

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

@register.simple_tag
def converto_to_hours(amount):
    hours = amount//60
    minutes = amount%60
    return {'hours':hours,'minutes':minutes}


