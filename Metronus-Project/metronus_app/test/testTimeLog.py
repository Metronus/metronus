from metronus_app.model.task import Task
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
from django.test import TestCase, Client
from populate_database import populate_database
from datetime import datetime,timedelta
from django.utils import timezone
import json

class TimeLogTestCase(TestCase):
    """This class provides a test case for using and managing employee timelogs"""
    @classmethod
    def setUpTestData(cls):
        """
        Loads the data to the database for tests to be done
        """
        populate_database()
    def test_list_timelog(self):
        """
        Common access to timelog list
        """
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/timeLog/list_all/")
        self.assertEquals(response.status_code, 200)

        today=datetime.today()
        #Check the tasks belong to me!
        self.assertEquals(response.context["currentDay"], today.day)
        self.assertEquals(response.context["currentMonth"], today.month)
        self.assertEquals(response.context["currentYear"], today.year)
        self.assertEquals(response.context["valid_production_units"], True)

        self.assertEquals(response.context["form"] is not None, True)
    def test_list_timelog_with_dates(self):
        """
        Common access to timelog list with specific dates
        """
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/timeLog/list_all/?currentDay=1&currentMonth=2&currentYear=2017")
        self.assertEquals(response.status_code, 200)

        self.assertEquals(response.context["currentDay"], 1)
        self.assertEquals(response.context["currentMonth"], 2)
        self.assertEquals(response.context["currentYear"], 2017)
        self.assertEquals(response.context["valid_production_units"], True)

        self.assertEquals(response.context["form"] is not None, True)
    def test_create_timelog_positive(self):
        """ Creates a timelog"""
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
        """Creates a timelog twice with different description, with production goals"""
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
        """ Creates a timelog twice with the same description, causing the log to be update"""
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
        """Creates a timelog without production goals when the task requires it"""
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
    
    def test_get_departments_no_project(self):
        """
        try get departments without project
        """
        c = Client()
        c.login(username="anddonram", password="123456")
        
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = c.post("/timeLog/list_all/", {
              "department":Department.objects.get(name="Backend").id,
              },**kwargs)
        self.assertEquals(response.status_code, 400)
    def test_get_departments_no_project_2(self):
        """
        try get departments without project, blank string
        """
        c = Client()
        c.login(username="anddonram", password="123456")
        
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = c.post("/timeLog/list_all/", {"project":"",
              "department":Department.objects.get(name="Backend").id,
              },**kwargs)
        self.assertEquals(response.status_code, 400)
            
    def test_get_departments(self):
        """
        get departments for select options in project
        """  
        c = Client()
        c.login(username="anddonram", password="123456")
        
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = c.post("/timeLog/list_all/", {
            "project":Project.objects.get(name="Metronus").id,
              },**kwargs)
        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)
        names=[]
        for dep in data:
            names.append(dep['fields']['name'])
        self.assertIn("Backend",names)
        self.assertNotIn("Frontend",names)
    def test_get_departments_2(self):
        """
        get departments for select options in project, department as blank string
        """  
        c = Client()
        c.login(username="anddonram", password="123456")
        
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = c.post("/timeLog/list_all/", {"department":"",
            "project":Project.objects.get(name="Metronus").id,
              },**kwargs)
        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)
        names=[]
        for dep in data:
            names.append(dep['fields']['name'])
        self.assertIn("Backend",names)
        self.assertNotIn("Frontend",names)

    def test_get_tasks(self):
        """
        get tasks for select options
        """  
        c = Client()
        c.login(username="anddonram", password="123456")
        
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = c.post("/timeLog/list_all/", {
            "project":Project.objects.get(name="Metronus").id,
            "department":Department.objects.get(name="Backend").id,
              },**kwargs)
        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)
        names=[]
        for task in data:
            names.append(task['fields']['name'])
        self.assertIn("Hacer cosas",names)
        self.assertNotIn("Hacer cosas de cua",names)
    def test_get_tasks_negative_no_project(self):
        """
        get tasks for select options, blank project
        """  
        c = Client()
        c.login(username="anddonram", password="123456")
        
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = c.post("/timeLog/list_all/", {
            "project":"",
            "department":Department.objects.get(name="Backend").id,
              },**kwargs)
        self.assertEquals(response.status_code, 400)
    def test_create_timelog_negative_2(self):
        """ Creates a timelog with production goals when the task does not need it"""
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
        """ Creates two timelogs whose sum overpasses the limit of 1440 minutes per day"""
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

    def test_delete_timelog(self):
        """
        delete a timelog
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before=TimeLog.objects.all().count()
        response = c.get("/timeLog/delete/{0}/".format(TimeLog.objects.filter(employee_id__user__username="ddlsb").first().id))
        self.assertEquals(response.status_code, 302)

        logs_after=TimeLog.objects.all().count()

        self.assertEquals(logs_before,logs_after+1)

    def test_delete_timelog_negative(self):
        """
        try deleting a timelog whose date has passed
        """
        c = Client()
        c.login(username="ddlsb", password="123456")
        response = c.get("/timeLog/delete/{0}/".format(TimeLog.objects.filter(employee_id__user__username="ddlsb",
                                                                              registryDate__lt=timezone.make_aware(datetime.today()-timedelta(days=1), timezone.get_current_timezone())).first().id))
        self.assertEquals(response.status_code, 403)
