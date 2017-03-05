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
from django.conf.urls import url
from django.contrib import admin
from metronus_app import views
from metronus_app.controllers import departmentController
urlpatterns = [
    url(r'^$', views.index),
	url(r'^index.html/$', views.index),
    url(r'^department/create$', departmentController.create),
    url(r'^department/list$', departmentController.list),
    url(r'^department/update$', departmentController.update),
    url(r'^department/delete$', departmentController.delete),
]
