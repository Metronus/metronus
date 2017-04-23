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
    """
    Creates a custom site for django superuser, for app use, statistics, etc.
    """
    site_header = 'Metronus administration'
    def get_urls(self):
        """
        Adds the new urls
        """
        urls = super().get_urls()
        my_urls = [
            url(r'^dashboard/$', self.admin_view(self.dashboard))
        ]
        return my_urls + urls

    def dashboard(self, request):
        """
        Returns a JSON which contains the number of tasks per company, 
        as well as the number of users currently logged
        """
        employees=list(Company.objects.all().annotate(num_emp=Count("actor")).values_list("id","num_emp"))
        context = {"employees":employees}
        sessions=Session.objects.all()
        users=[]
        for s in sessions:
            u=User.objects.get(pk=s.get_decoded()['_auth_user_id'])
            users.append(u.id)
        #logged users
        context["users"]=users

        #task by company
        context["tasks"]=list(Company.objects.all().annotate(num_task=Count("project__projectdepartment__task")).values_list("id","num_task"))
        return JsonResponse(context)#(request, "dashboard.html", context)


class MyModelAdmin(admin.ModelAdmin):
    """
    I think this now does nothing, so maybe it can be removed
    """
    pass
admin_site = MyAdminSite(name='myadmin')
