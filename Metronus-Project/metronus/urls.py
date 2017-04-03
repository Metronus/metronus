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
from django.contrib.auth.views      import password_reset, password_reset_complete, password_reset_confirm, password_reset_done
from metronus_app.admin             import admin_site
from django.conf.urls.i18n          import i18n_patterns
from metronus_app                   import views
from django.core.urlresolvers       import reverse_lazy

from metronus_app.controllers       import appController
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
from metronus_app.controllers       import dashboardController
from metronus.settings              import DEFAULT_FROM_EMAIL, MEDIA_ROOT, MEDIA_URL

from django.conf.urls.static import static


urlpatterns = [url(r'^i18n/', include('django.conf.urls.i18n')),
                url(r'^admin/', admin_site.urls),]
urlpatterns += [#i18n_patterns(

    url(r'^$', views.index),
    url(r'^index.html/$', views.index, name='home'),
    url(r'^app/$', appController.index, name='app_index'),
 
    #Department
    url(r'^department/create$', departmentController.create, name='department_create'),
    url(r'^department/createAsync$', departmentController.createAsync),
    url(r'^department/list$', departmentController.list, name='department_list'),
    url(r'^department/edit/(?P<department_id>\w{0,50})/$', departmentController.edit, name='department_edit'),
    url(r'^department/view/(?P<department_id>\w{0,50})/$', departmentController.view, name='department_view'),
    url(r'^department/delete/(?P<department_id>\w{0,50})/$', departmentController.delete, name='department_delete'),
    url(r'^department/ajaxEmployeesPerTask$', departmentController.ajax_employees_per_task, name='department_employees_per_task'),
    url(r'^department/ajaxTimePerTask$', departmentController.ajax_time_per_task, name='department_time_per_task'),

    #Task
    url(r'^task/create$', taskController.create, name='task_create'),
    url(r'^task/createAsync$', taskController.createAsync),
    url(r'^task/list$', taskController.list, name='task_list'),
    url(r'^task/view/(?P<task_id>\w{0,50})/$', taskController.view, name='task_view'),
    url(r'^task/edit/(?P<task_id>\w{0,50})/$', taskController.edit, name='task_edit'),
    url(r'^task/delete/(?P<task_id>\w{0,50})/$', taskController.delete, name='task_delete'),
    url(r'^task/getdepartments$', taskController.form_departments),

    #Project
    url(r'^project/list$', projectController.list, name='project_list'),
    url(r'^project/edit/(?P<project_id>\w{0,50})/$', projectController.edit, name='project_edit'),
    url(r'^project/show/(?P<project_id>\w{0,50})/$', projectController.show, name='project_show'),
    url(r'^project/delete/(?P<project_id>\w{0,50})/$', projectController.delete, name='project_delete'),
    url(r'^project/create$', projectController.create, name='project_create'),
    url(r'^project/createAsync$', projectController.createAsync, name='project_create_async'),
    url(r'^project/ajaxEmployeesPerDpmt$', projectController.ajax_employees_per_department, name='project_employees_per_department'),
    url(r'^project/ajaxTasksPerDpmt$', projectController.ajax_tasks_per_department, name='project_tasks_per_department'),
    url(r'^project/ajaxTimePerDpmt$', projectController.ajax_time_per_department, name='project_time_per_department'),

    #Project-Department relationship
    url(r'^projectdepartment/create$', projectDepartmentController.create, name='projectdepartment_create'),
    url(r'^projectdepartment/list$', projectDepartmentController.list, name='projectdepartment_list'),
    #url(r'^projectdepartment/edit$', projectDepartmentController.edit, name='projectdepartment_edit'),No necesario, en un principio
    url(r'^projectdepartment/delete$', projectDepartmentController.delete, name='projectdepartment_delete'),

    #Employee
    url(r'^employee/create$', employeeController.create, name='employee_create'),
    url(r'^employee/list$', employeeController.list, name='employee_list'),
    url(r'^employee/view/(?P<username>\w{0,50})/$', employeeController.view, name='employee_view'),
    url(r'^employee/edit/(?P<username>\w{0,50})/$', employeeController.edit, name='employee_edit'),
    url(r'^employee/updatePassword/(?P<username>\w{0,50})/$', employeeController.updatePassword, name='employee_updatePassword'),
    url(r'^employee/delete/(?P<username>\w{0,50})/$', employeeController.delete, name='employee_delete'),

    # TimeLogs
    url(r'^timeLog/list_all/$', timeLogController.list_all, name='timeLog_list_all'),
    url(r'^timeLog/list/(?P<task_id>\w{0,50})/$', timeLogController.list, name='timeLog_list'),
    url(r'^timeLog/create/(?P<task_id>\w{0,50})/$', timeLogController.create_by_task, name='timeLog_create_by_task'),
    url(r'^timeLog/create_all/$', timeLogController.create_all, name='timeLog_create_all'),
    url(r'^timeLog/edit/(?P<timeLog_id>\w{0,50})/$', timeLogController.edit, name='timeLog_edit'),
    url(r'^timeLog/delete/(?P<timeLog_id>\w{0,50})/$', timeLogController.delete, name='timeLog_delete'),

    # Roles
    url(r'^roles/manage$', roleController.manage, name='roles_manage'),
    url(r'^roles/manageAsync$', roleController.manageAsync, name='roles_manageAsync'),
    url(r'^roles/delete/(?P<role_id>\d{0,50})/$', roleController.delete, name='roles_delete'),
    url(r'^roles/availableDepartments', roleController.ajax_departments_from_projects, name='roles_dpmt_ajax'),
    url(r'^roles/availableRoles', roleController.ajax_roles_from_tuple, name='roles_role_ajax'),

    # Administrator
    url(r'^administrator/edit/(?P<username>\w{0,50})/$', administratorController.edit, name='administrator_edit'),
    # url(r'^administrator/view/(?P<username>\w{0,50})/$', administratorController.view, name='administrator_edit'),

    # Company
    url(r'^company/edit/$', companyController.edit, name='company_edit'),
    url(r'^company/view/$', companyController.view, name='company_view'),
    url(r'^company/delete/$', companyController.view, name='company_delete'),

    #Dashboard
    url(r'^dashboard/ajaxTimePerProject$', dashboardController.ajax_time_per_project, name='dashboard_time_per_project'),
    url(r'^dashboard/ajaxEmployeesPerProject$', dashboardController.ajax_employees_per_project, name='dashboard_employees_per_project'),
    url(r'^dashboard/ajaxDepartmentsPerProject$', dashboardController.ajax_departments_per_project, name='dashboard_departments_per_project'),
    
    # Login
    url(r'^login/$', loginController.login, {'template_name': 'login.html', }, name="login"),
    url(r'^logout/$', loginController.logout, {'next_page': '/', }, name="logout"),
    url(r'^(?P<company>\w{0,50})/', include([
        url(r'^login/$', loginController.login, {'template_name': 'login.html', }, name="login"),
    ])),

    # Pass recovery
    url(r'^lost-password/$', password_reset, {'template_name': 'auth/password_reset.html',
        'post_reset_redirect': '/reset-password/', 'from_email': DEFAULT_FROM_EMAIL,
        'email_template_name': 'auth/password_reset_email.html',
        'subject_template_name': 'auth/password_reset_subject.txt',
        'html_email_template_name': 'auth/password_reset_email.html'}
        , name='password_reset'),
    url(r'^reset-password/$', password_reset_done, {'template_name': 'auth/info_reset_password.html'}
        , name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm,
        {'template_name': 'auth/password_reset_confirm.html', 'post_reset_redirect': '/reset-done/'}
        , name='password_reset_confirm'),
    url(r'^reset-done/$', password_reset_complete, {'template_name': 'auth/password_reset_complete.html'}
        , name='password_reset_complete'),

    url(r'^contact/$', appController.contact, name='contact'),
    url(r'^contact-done/$', appController.contact_done, name='contact_done'),

    url(r'^register$', companyController.create),
    url(r'^ajax/validate_cif/$', companyController.validateCIF, name='validate_cif'),
    url(r'^ajax/validate_admin/$', companyController.validateAdmin, name='validate_admin'),
    url(r'^ajax/validate_short_name/$', companyController.validateShortName, name='validate_short_name'),

#)
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
