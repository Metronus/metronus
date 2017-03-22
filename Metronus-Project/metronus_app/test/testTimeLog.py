from metronus_app.model.task import Task
from django.contrib.auth.models                  import User
from metronus_app.model.timeLog import TimeLog
from django.test import TestCase, Client
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from metronus_app.controllers.timeLogController import *
from populate_database import populate_database

class TaskTestCase(TestCase):

    def setUpTestData():
        populate_database()

    def createTimeLogPositive(self):
        c = Client()
        c.login(username="andjimrio", password="123456")

        before = TimeLog.objects.all().count()
