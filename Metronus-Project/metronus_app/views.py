from django.shortcuts import render
import metronus_app.controllers.departmentController
import metronus_app.controllers.projectController
import time

# Create your views here.

def index(request):
	return render(request, "index.html", {"current_date": time.strftime("%Y-%m-%d %H:%M")})
