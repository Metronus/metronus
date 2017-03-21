from metronus_app.model.department import Department
from metronus_app.model.company import Company
from metronus_app.model.task import Task
from metronus_app.controllers.departmentController import *
from django.contrib.auth.models                  import User
from django.test import TestCase, Client
from metronus_app.model.employee         import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from populate_database import populate_database
class TaskTestCase(TestCase):

    def setUpTestData():
        populate_database()

    def test_create_task_positive(self):
        # Logged in as an administrator, try to create a task
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = Task.objects.all().count()
        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id

        response = c.post("/task/create", {
            "task_id": "0",
            "name": "dep4",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id
              })

        self.assertEquals(response.status_code, 302)

        # Check that the task has been successfully created

        dep = Task.objects.all().last()
        self.assertEquals(dep.name, "dep4")
        self.assertEquals(dep.active,True)
        logs_after = Task.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_task_duplicate(self):
        # Logged in as an administrator, try to create an task with the name of an existing company
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = Task.objects.all().count()

        response = c.post("/task/create", {
            "task_id": "0",
            "description":"alguno",
            "name": "Hacer cosas",
            "project_id":str(Project.objects.get(name="Metronus").id),
            "department_id":str(Department.objects.get(name="Backend").id)
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["repeated_name"],True)


    def test_create_task_not_logged(self):
        c = Client()
        response = c.get("/task/create")
        self.assertEquals(response.status_code, 403)

    def test_create_task_not_allowed(self):
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/task/create")
        self.assertEquals(response.status_code, 403)


    def test_list_tasks_positive(self):
        c = Client()
        c.login(username="ddlsb", password="123456")

        response = c.get("/task/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["tasks"]), 3)

    def test_list_tasks_positive_2(self):
        c = Client()
        c.login(username="Barrelito", password="123456")
        response = c.get("/task/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["tasks"]), 1)

    def test_list_tasks_not_logged(self):
        c = Client()
        response = c.get("/task/list")
        self.assertEquals(response.status_code, 403)

    def test_view_task_positive(self):
        c = Client()
        c.login(username="agubelu", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["task"]

        self.assertEquals(form.id, dep_id)


    def test_view_task_positive_2(self):
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["task"]

        self.assertEquals(form.id, dep_id)

    def test_view_task_negative(self):
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id

        c.logout()
        c.login(username="andjimrio", password="123456")
        response = c.get("/task/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_edit_task_get(self):
        c = Client()
        c.login(username="agubelu", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/edit/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["task_id"], dep_id)

    def test_edit_task_404(self):
        c = Client()
        c.login(username="anddonram", password="123456")

        response = c.get("/task/edit?task_id=9000")
        self.assertEquals(response.status_code, 404)


    def test_delete_task_positive(self):
        c = Client()
        c.login(username="agubelu", password="123456")

        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id

        response = c.get("/task/delete/"+str(dep_id)+"/")
        self.assertRedirects(response, "/task/list", fetch_redirect_response=False)

        self.assertFalse(Task.objects.get(pk=dep_id).active)

    def test_delete_task_not_allowed(self):
        c = Client()
        c.login(username="andjimrio", password="123456")
        task=Task.objects.filter(name="Hacer cosas de back").first()
        response = c.get("/task/delete/"+str(task.id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_delete_task_not_active(self):
        c = Client()
        c.login(username="ddlsb", password="123456")

        dep_id=Task.objects.filter(active=False).first().id
        response = c.get("/task/delete/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 404)
