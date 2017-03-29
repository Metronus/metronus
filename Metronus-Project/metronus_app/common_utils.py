from django.core.exceptions                      import PermissionDenied
from metronus_app.model.administrator            import Administrator
from metronus_app.model.employee                 import Employee
from django.core.exceptions                      import ObjectDoesNotExist
from metronus.settings                           import DEFAULT_FROM_EMAIL
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.template import loader
from django.core.mail import EmailMultiAlternatives

from PIL import Image


# Image limit parameters
FILE_SIZE = 100000000
HEIGHT = 256
WIDTH = 256
VALID_FORMATS = ['JPEG', 'JPG', 'PNG']


def get_current_admin_or_403(request):
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied


def get_current_employee_or_403(request):

    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Employee.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied

def get_authorized_or_403(request):
    # Returns the current administrator, or the logged user if they have at least a role higher than Employee on any department/project

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
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def check_company_contains_actor(company, username):
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


def send_mail(subject, email_template_name, recipients, html_email_template_name, context, **kwargs):

    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, DEFAULT_FROM_EMAIL, recipients)
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send(fail_silently=False)
