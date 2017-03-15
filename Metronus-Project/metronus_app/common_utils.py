from django.core.exceptions                      import PermissionDenied
from metronus_app.model.administrator            import Administrator
from metronus_app.model.employee            import Employee
from django.core.exceptions                      import ObjectDoesNotExist


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
