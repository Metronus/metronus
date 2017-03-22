from django.shortcuts import render
from django.core.exceptions                      import PermissionDenied
from django.http import HttpResponseRedirect
def index(request):
    """
    returns:
    to be redirected after login

    template:
    app_index.html
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/login/")

    return render(request, "app_index.html")
