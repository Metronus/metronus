from django.core.exceptions                      import PermissionDenied
from metronus_app.model.administrator            import Administrator
from django.core.exceptions                      import ObjectDoesNotExist

def get_current_admin_or_403(request):
    if not request.user.is_authenticated():
        raise PermissionDenied
    try:
        return Administrator.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied