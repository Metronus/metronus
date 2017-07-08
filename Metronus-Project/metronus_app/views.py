from django.shortcuts import render
from django.http import HttpResponseRedirect
from random import random

def index(request):
    if request.user.is_authenticated():
        url = {
            'A': "/dashboard/view",
            'E': "/timeLog/list_all",
        }.get(request.user.actor.user_type, "/app/")
        return HttpResponseRedirect(url)
    else:
        return render(request, "index.html")


handler400 = 'metronus_app.views.bad_request'
handler403 = 'metronus_app.views.permission_denied'
handler404 = 'metronus_app.views.page_not_found'
handler500 = 'metronus_app.views.error'

####################################################
#          DON'T OPEN, DEAD PAGES INSIDE           #
####################################################
def bad_request(request):
    """ Error 400 """
    return error_view(request, 'error400.html', 400)

def permission_denied(request):
    """ Error 403 """
    return error_view(request, 'error403.html', 403)

def page_not_found(request):
    """ Error 404 """
    return error_view(request, 'error404.html', 404)

def error(request):
    """ Error 500 """
    return error_view(request, 'error500.html', 500)

def error_view(request, html_file, status):
    """ Returns an error view """
    return render(request, "error/" + html_file, {'img' : error_gif()}, status = status)

def error_gif():
    return '/static/img/error_' + str(round(random())) + ".gif"
