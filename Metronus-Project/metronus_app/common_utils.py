from django.core.exceptions import PermissionDenied
from metronus_app.model.administrator import Administrator
from metronus_app.model.employee import Employee
from metronus.settings import DEFAULT_FROM_EMAIL,AUTH_PASSWORD_VALIDATORS
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from metronus_app.model.timeLog import TimeLog
from django.core.exceptions import ObjectDoesNotExist
from metronus_app.model.company import Company
from metronus_app.model.role import Role
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.task import Task
from django.test import Client
from django.contrib.auth.password_validation import validate_password, ValidationError,get_password_validators
from PIL import Image

import sys
import string
import random
import json


# Image limit parameters
FILE_SIZE = 100000000
HEIGHT = 256
WIDTH = 256
VALID_FORMATS = ['JPEG', 'JPG', 'PNG']

def validate_pass(password):
    """
    checks if the password is valid
    """
    try:
        validate_password(password,get_password_validators(AUTH_PASSWORD_VALIDATORS))
    except ValidationError:
        return False
    return True

def default_round(val,dig=2):
    """
    rounds to two decimal digits
    """
    return None if val is None else round(val,dig)

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
def get_admin_executive_or_403(request):
    """
    Returns the current administrator,
    or the executive if it is logged
    """
    if not request.user.is_authenticated():
        raise PermissionDenied

    try:
        return get_current_admin_or_403(request)
    except PermissionDenied:
        # The user is authenticated and it's not an admin
        cur_user = Employee.objects.get(user=request.user)
        if ProjectDepartmentEmployeeRole.objects.filter(employee_id=cur_user, role_id__tier__gte=50).count() > 0:
            return cur_user
        else:
            raise PermissionDenied


def is_executive(employee):
    if employee.user_type != "E":
        return False
    return ProjectDepartmentEmployeeRole.objects.filter(employee_id=employee, role_id__tier__gte=50).count() > 0


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


def check_image(form, param):
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
              context, email_from=DEFAULT_FROM_EMAIL):
    """
    Sends an email to someone
    """
    if 'test' in sys.argv:
        return  # Don't send mails if we are testing to prevent spam

    if context['html']:
        body = loader.render_to_string(email_template_name, context)
    else:
        body = email_template_name

    email_message = EmailMultiAlternatives(subject, body, email_from, recipients)
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send(fail_silently=True)


def is_username_unique(username):
    """
    Check the username is unique and does not exists in the database
    """
    return User.objects.filter(username=username).count() == 0

def email_in_use_logged(email, user):
    """ Checks if a email is used by a user who is not me """
    return User.objects.filter(email=email).exclude(pk=user.pk).count() == 0

def is_email_unique(email):
    """
    Checks the email is unique and does not exists in the database
    """
    return User.objects.filter(email=email).count() == 0


def is_company_email_unique(email):
    """
    Checks the company email is unique and does not exists in the database
    """
    return Company.objects.filter(email=email).count() == 0


def is_cif_unique(cif):
    """
    Checks the CIF is unique and does not exists in the database
    """
    return Company.objects.filter(cif=cif).count() == 0

def ranstr():
    """ Returns a 10-character random string"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


# Son herramientas sorpresa que nos ayudarán más tarde

def check_json_metrics_are_equal(self, response_string, data):
    """
    Checks the data provided by the JSON equals the real data
    """
    response = json.loads(response_string)

    self.assertTrue('names' in response)
    self.assertTrue('values' in response)

    self.assertEquals(len(response['names']), len(data['names']))
    self.assertEquals(len(response['values']), len(data['values']))

    for name, val in zip(data['names'], data['values']):
        self.assertTrue(name in response['names'])
        self.assertTrue(val in response['values'])

        ind = response['names'].index(name)

        self.assertEquals(val, response['values'][ind])


def create_employee_in_projdept(project, department):
    """
    creates an employee and assigns him/her a new role
    """
    user = User.objects.create_user(
        username=ranstr(),
        password=ranstr(),
        email=ranstr() + "@metronus.es",
        first_name=ranstr(),
        last_name=ranstr()
    )

    employee = Employee.objects.create(
        user=user,
        user_type="E",
        identifier=ranstr(),
        phone="123123123",
        company_id=Company.objects.get(company_name="company1")
    )

    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

    role = Role.objects.get(tier=random.choice([10, 20, 30, 40, 50]))
    ProjectDepartmentEmployeeRole.objects.create(projectDepartment_id=pd, role_id=role, employee_id=employee)

    return employee


def create_task_in_projdept(project, department,admin=None):
    """
    creates a task for a given project and department, either with production goal or not
    """
    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

    Task.objects.create(
        name=ranstr(),
        description=ranstr(),
        actor_id=Administrator.objects.get(identifier="adm01") if admin is None else admin,
        projectDepartment_id=pd
    )

def create_timelog_in_task(task, duration, date, employee=None):
    """
    creates a timelog for an employee involving a task during a specific date
    """
    TimeLog.objects.create(
        description=ranstr(),
        workDate=date,
        duration=duration,
        task_id=task,
        employee_id=Employee.objects.get(identifier="emp01") if employee is None else employee
    )


def get_ajax(url, data = None):
    """
    Function to automatize the process of getting the ajax response from a source
    """
    c = Client()
    response = c.get(url, data)
    return json.loads(response.content.decode("utf-8"))


def is_role_updatable_by_user(logged, pdrole_id):
    """
    Determines whether the provided user can update/delete the role with the given ID
    """
    pdrole = get_or_none(ProjectDepartmentEmployeeRole, id=pdrole_id)

    # Check that it exists and belongs to the logged user's company
    if not pdrole or pdrole.employee_id.company_id != logged.company_id:
        return False

    # Admins can always do whatever the fuck they want
    if logged.user_type == "A":
        return True

    # Only admins and executives can edit role
    if not is_executive(logged):
        return False

    # If it belongs to the same user, check that it's not their highest role
    if pdrole.employee_id == logged:
        return ProjectDepartmentEmployeeRole.objects.filter(employee_id=logged, role_id__tier__gt=pdrole.role_id.tier).exists()
    # If it belongs to someone else, check that the role they're trying to edit is not Executive
    # Because only executives and administrator can manage roles, then execs can edit anything below their level
    else:
        return pdrole.role_id.tier < 50
