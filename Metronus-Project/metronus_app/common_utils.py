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
