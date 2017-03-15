"""metronus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls               import url, include
from django.contrib                 import admin
from metronus_app.admin                 import admin_site
from django.conf.urls.i18n          import i18n_patterns
from metronus_app                   import views
from django.core.urlresolvers       import reverse_lazy

from metronus_app.controllers       import departmentController
from metronus_app.controllers       import projectController
from metronus_app.controllers       import projectDepartmentController
from metronus_app.controllers       import employeeController
from metronus_app.controllers       import roleController
from metronus_app.controllers       import companyController
from metronus_app.controllers       import administratorController
from metronus_app.controllers       import taskController
from metronus_app.controllers       import timeLogController
from metronus_app.controllers       import loginController


urlpatterns = [url(r'^i18n/', include('django.conf.urls.i18n')),
                url(r'^admin/', admin_site.urls),]
urlpatterns += [#i18n_patterns(

    url(r'^$', views.index),
    url(r'^index.html/$', views.index, name='home'),

    url(r'^department/create$', departmentController.create),
    url(r'^department/createAsync$', departmentController.createAsync),
    url(r'^department/list$', departmentController.list),
    url(r'^department/edit$', departmentController.edit),
    url(r'^department/view$', departmentController.view),
    url(r'^department/delete$', departmentController.delete),

    #a la espera de ponerle el name
    url(r'^task/create$', taskController.create),
    url(r'^task/list_project$', taskController.list_project),
    url(r'^task/list_department$', taskController.list_department),
    url(r'^task/edit$', taskController.edit),
    url(r'^task/delete$', taskController.delete),

    url(r'^project/list$', projectController.list, name='project_list'),
    url(r'^project/edit/(?P<project_id>\w{0,50})/$', projectController.edit, name='project_edit'),
    #url(r'^project/view$', projectController.view), A la espera de ver si es necesario o no
    url(r'^project/delete/(?P<project_id>\w{0,50})/$', projectController.delete, name='project_delete'),
    url(r'^project/create$', projectController.create, name='project_create'),

    url(r'^projectdepartment/create$', projectDepartmentController.create, name='projectdepartment_create'),
    url(r'^projectdepartment/list$', projectDepartmentController.list, name='projectdepartment_list'),
    #url(r'^projectdepartment/edit$', projectDepartmentController.edit, name='projectdepartment_edit'),No necesario, en un principio
    url(r'^projectdepartment/delete$', projectDepartmentController.delete, name='projectdepartment_delete'),

    url(r'^employee/create$', employeeController.create, name='employee_create'),
    url(r'^employee/list$', employeeController.list, name='employee_list'),
    url(r'^employee/view/(?P<username>\w{0,50})/$', employeeController.view, name='employee_view'),
    url(r'^employee/edit/(?P<username>\w{0,50})/$', employeeController.edit, name='employee_edit'),
    url(r'^employee/delete/(?P<username>\w{0,50})/$', employeeController.delete, name='employee_delete'),

    # TimeLogs
    url(r'^timeLog/list/(?P<task_id>\w{0,50})/$', timeLogController.list, name='timeLog_list'),
    url(r'^timeLog/create/(?P<task_id>\w{0,50})/$', timeLogController.create, name='timeLog_create'),
    url(r'^timeLog/edit/(?P<timeLog_id>\w{0,50})/$', timeLogController.edit, name='timeLog_edit'),
    url(r'^timeLog/delete/(?P<timeLog_id>\w{0,50})/$', timeLogController.delete, name='timeLog_delete'),

    url(r'^roles/manage$', roleController.manage, name='roles_manage'),

    # Administrator
    url(r'^administrator/edit/(?P<username>\w{0,50})/$', administratorController.edit, name='administrator_edit'),
    url(r'^administrator/view/(?P<username>\w{0,50})/$', administratorController.view, name='administrator_edit'),

    # Company
    url(r'^company/edit/(?P<cif>\w{9})/$', companyController.edit, name='company_edit'),
    url(r'^company/view/(?P<cif>\w{9})/$', companyController.view, name='company_view'),

    # Login
    url(r'^login/$', loginController.login, {'template_name': 'login.html', }, name="login"),
    url(r'^(?P<company>\w{0,50})/', include([
        url(r'^login/$', loginController.login, {'template_name': 'login.html', }, name="login"),
    ])),
    url(r'^logout/$', loginController.logout, {'next_page': reverse_lazy('home'), }, name="logout"),

    url(r'^register$', companyController.create),
    url(r'^ajax/validate_cif/$', companyController.validateCIF, name='validate_cif'),
    url(r'^ajax/validate_admin/$', companyController.validateAdmin, name='validate_admin'),

#)
]