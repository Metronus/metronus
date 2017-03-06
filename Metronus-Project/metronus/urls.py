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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from metronus_app import views
from metronus_app.controllers import departmentController
from metronus_app.controllers import projectController

urlpatterns = i18n_patterns(
    url(r'^$', views.index),
    url(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^index.html/$', views.index),
    url(r'^department/create$', departmentController.create),
    url(r'^department/list$', departmentController.list),
    url(r'^department/update$', departmentController.update),
    url(r'^department/delete$', departmentController.delete),

    url(r'^project/list$', projectController.list),
    url(r'^project/edit$', projectController.edit),
    #url(r'^project/view$', projectController.view), A la espera de ver si es necesario o no
    url(r'^project/delete$', projectController.delete),
    url(r'^project/create$', projectController.create),
)
