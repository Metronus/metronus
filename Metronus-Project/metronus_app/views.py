from django.shortcuts import render
import metronus_app.view.departmentView
import time

# Create your views here.

def index(request):
	return render(request, "index.html", {"current_date": time.strftime("%Y-%m-%d %H:%M")})
