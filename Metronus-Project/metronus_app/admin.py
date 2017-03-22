from django.contrib import admin
from django.http import JsonResponse
from metronus_app.model.employee import Employee
from metronus_app.model.task import Task
from metronus_app.model.company import Company
from django.conf.urls               import url, include
# Register your models here.
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.contrib.sessions.models import Session
from django.contrib.auth.models                  import User
from django.db.models import Count
class MyAdminSite(AdminSite):
    site_header = 'Metronus administration'
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^dashboard/$', self.admin_view(self.dashboard))
        ]
        return my_urls + urls

    def dashboard(self, request):
        # ...
        employees=list(Company.objects.all().annotate(num_emp=Count("actor")).values_list("id","num_emp"))
        context = {"employees":employees}
        sessions=Session.objects.all()
        users=[]
        for s in sessions:
            u=User.objects.get(pk=s.get_decoded()['_auth_user_id'])
            users.append(u.id)
        #logged users
        context["users"]=users
        print(users)

        #task by company
        context["tasks"]=list(Company.objects.all().annotate(num_task=Count("project__projectdepartment__task")).values_list("id","num_task"))
        print(context["tasks"])
        return JsonResponse(context)#(request, "dashboard.html", context)


class MyModelAdmin(admin.ModelAdmin):
    pass
admin_site = MyAdminSite(name='myadmin')
