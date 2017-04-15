from metronus_app.model.task import Task
from django.contrib.auth.models                  import User
from metronus_app.model.timeLog import TimeLog
from django.test import TestCase, Client
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from metronus_app.controllers.timeLogController import *
from populate_database import populate_database

class TimeLogTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        populate_database()

    def test_create_timelog_positive(self):
        # Creates a timelog
        c = Client()
        c.login(username="anddonram", password="123456")
        task=Task.objects.filter(name="Hacer cosas de back").first()

        logs_before = TimeLog.objects.all().count()

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":2.0,
            "workDate":datetime.today()
            #"produced_units":None
              })

        self.assertEquals(response.status_code, 302)
        # Check that the task has been successfully created

        log = TimeLog.objects.all().last()
        self.assertEquals(log.description, "alguno")
        self.assertEquals(log.duration,2.0)
        logs_after = TimeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)


    def test_create_timelog_positive_2(self):
        # Creates a timelog twice with different description, with production goals
        c = Client()
        c.login(username="andjimrio", password="123456")
        task=Task.objects.filter(name="Hacer cosas de front").first()

        logs_before = TimeLog.objects.all().count()

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":2.0,
            "produced_units":2.0,
            "workDate":datetime.today()
              })

        self.assertEquals(response.status_code, 302)
        # Check that the task has been successfully created

        log = TimeLog.objects.all().last()
        self.assertEquals(log.description, "alguno")
        self.assertEquals(log.duration,2.0)
        self.assertEquals(log.produced_units,2.0)
        logs_after = TimeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"algno",
            "duration":2.0,
            "produced_units":0.5,
            "workDate":datetime.today()
              })

        self.assertEquals(response.status_code, 302)

        # Check that the task has been successfully updated

        log = TimeLog.objects.all().last()
        self.assertEquals(log.description, "algno")
        self.assertEquals(log.duration,4.0)
        self.assertEquals(log.produced_units,2.5)
        logs_after = TimeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

        

    def test_create_timelog_positive_3(self):
        # Creates a timelog twice with the same description, causing the log to be update
        c = Client()
        c.login(username="andjimrio", password="123456")
        task=Task.objects.filter(name="Hacer cosas de front").first()

        logs_before = TimeLog.objects.all().count()

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":2.0,
            "produced_units":2.0,
            "workDate":datetime.today()
              })

        self.assertEquals(response.status_code, 302)
        # Check that the task has been successfully created

        log = TimeLog.objects.all().last()
        self.assertEquals(log.description, "alguno")
        self.assertEquals(log.duration,2.0)
        self.assertEquals(log.produced_units,2.0)
        logs_after = TimeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":2.0,
            "produced_units":0.5,
            "workDate":datetime.today()
              })

        self.assertEquals(response.status_code, 302)

        # Check that the task has been successfully updated

        log = TimeLog.objects.all().last()
        self.assertEquals(log.description, "alguno")
        self.assertEquals(log.duration,4.0)
        self.assertEquals(log.produced_units,2.5)
        logs_after = TimeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)



    def test_create_timelog_negative(self):
        # Creates a timelog without production goals when the task requires it
        c = Client()
        c.login(username="andjimrio", password="123456")
        task=Task.objects.filter(name="Hacer cosas de front").first()


        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":2.0,
            "workDate":datetime.today()
              })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["valid_production_units"], False)
        self.assertEquals(response.context['over_day_limit'], False)

    def test_create_timelog_negative_2(self):
        # Creates a timelog with production goals when the task does not need it
        c = Client()
        c.login(username="anddonram", password="123456")
        task=Task.objects.filter(name="Hacer cosas de back").first()

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":2.0,
            "workDate":datetime.today(),
            "produced_units":30
              })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["valid_production_units"], False)
        self.assertEquals(response.context['over_day_limit'], False)

    def test_create_timelog_overtime(self):
        # Creates two timelogs whose sum overpasses the limit of 1440 minutes per day
        c = Client()
        c.login(username="andjimrio", password="123456")
        task=Task.objects.filter(name="Hacer cosas de front").first()

        logs_before = TimeLog.objects.all().count()

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"alguno",
            "duration":720.0,
            "produced_units":2.0,
            "workDate":datetime.today()
              })

        self.assertEquals(response.status_code, 302)
        # Check that the task has been successfully created

        log = TimeLog.objects.all().last()
        self.assertEquals(log.description, "alguno")
        self.assertEquals(log.duration,720.0)
        self.assertEquals(log.produced_units,2.0)
        logs_after = TimeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

        response = c.post("/timeLog/list_all/", {
        	"timeLog_id":0,
            "project_id":task.projectDepartment_id.project_id.id,
            "department_id":task.projectDepartment_id.department_id.id,
            "task_id": task.id,
            "description":"algno",
            "duration":1000.0,
            "produced_units":0.5,
            "workDate":datetime.today()
              })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['over_day_limit'], True)
