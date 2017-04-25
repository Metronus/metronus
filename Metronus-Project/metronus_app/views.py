from django.shortcuts import render
from django.http import HttpResponseRedirect
import time


# Create your views here.
def index(request):

    if request.user.is_authenticated():
        if request.user.actor.user_type == 'A':
            return HttpResponseRedirect("/dashboard/view")
        elif request.user.actor.user_type == 'E':
            return HttpResponseRedirect("/timeLog/list_all")
        else:
            return HttpResponseRedirect("/app/")
    else:
        return render(request, "index.html", {"current_date": time.strftime("%Y-%m-%d %H:%M")})

