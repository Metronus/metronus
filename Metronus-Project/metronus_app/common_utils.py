from django.core.exceptions                      import PermissionDenied
from metronus_app.model.administrator            import Administrator
from metronus_app.model.employee                 import Employee
from django.core.exceptions                      import ObjectDoesNotExist
from metronus.settings                           import DEFAULT_FROM_EMAIL
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models                  import User

from PIL import Image

import sys


# Image limit parameters
FILE_SIZE = 100000000
HEIGHT = 256
WIDTH = 256
VALID_FORMATS = ['JPEG', 'JPG', 'PNG']


def get_current_admin_or_403(request):
    """
    Returns logged admin or 403 if not logged or logged is not an admin
    """
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied


def get_current_employee_or_403(request):
    """
    Returns employee admin or 403 if not logged or logged is not an employee
    """

    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Employee.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

def get_authorized_or_403(request):
    """ 
    Returns the current administrator,
    or the logged user if they have at least a role higher than Employee on any department/project
    """
    if not request.user.is_authenticated():
        raise PermissionDenied

    try:
        return get_current_admin_or_403(request)
    except PermissionDenied:
        # The user is authenticated and it's not an admin
        cur_user = Employee.objects.get(user=request.user)
        if ProjectDepartmentEmployeeRole.objects.filter(employee_id=cur_user, role_id__tier__gt=10).count() > 0:
            return cur_user
        else:
            raise PermissionDenied


def get_or_none(model, *args, **kwargs):
    """
    Gets an instance of the model class from the database
    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def check_user_email(email):
    """
    Checks there is an user in the database with that email
    """
    try:
        User.objects.get(email=email)
        return True
    except User.DoesNotExist:
        return False


def check_company_contains_actor(company, username):
    """
    Checks the username belongs to an actor from the company passed as a parameter
    """
    ret = False
    actor_set = company.actor_set.all()
    if actor_set is not None:
        for actor in actor_set:
            if str(username) == str(actor.user.username):
                ret = True
        if ret is False:
            raise PermissionDenied


def checkImage(form, param):
    """
    checks if logo has the correct dimensions and extension
    """
    logo = form.cleaned_data[param]

    if logo is not None:
        image = Image.open(logo, mode="r")
        xsize, ysize = image.size
        ext = image.format in VALID_FORMATS

        return xsize <= WIDTH and ysize <= HEIGHT and ext
    else:
        return True


def send_mail(subject, email_template_name, recipients, html_email_template_name,
              context, email_from=DEFAULT_FROM_EMAIL, **kwargs):
    """
    Sends an email to someone
    """
    if 'test' in sys.argv: return # Don't send mails if we are testing to prevent spam

    if context['html']:
        body = loader.render_to_string(email_template_name, context)
    else:
        body = email_template_name

    email_message = EmailMultiAlternatives(subject, body, email_from, recipients)
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send(fail_silently=False)


def is_username_unique(username):
    """
    Check the username is unique and does not exists in the database
    """
    return User.objects.filter(username=username).count() == 0


def is_email_unique(email):
    """
    Checks the email is unique and does not exists in the database
    """
    return User.objects.filter(email=email).count() == 0