from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.contrib.auth.models import User
from metronus_app.model.administrator import Administrator
from metronus_app.model.task import Task
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.controllers.departmentController import *
from django.test import TestCase, Client
from django.core.exceptions                      import ObjectDoesNotExist, PermissionDenied
from populate_database import populate_database
import json

class DepartmentTestCase(TestCase):
    """This class provides a test case for department management"""
    @classmethod
    def setUpTestData(cls):
        company1 = Company.objects.create(
            cif="123",
            company_name = "company1",
            short_name="mplp",
            email= "company1@gmail.com",
            phone= "123456789"
        )

        company2 = Company.objects.create(
            cif="456",
            company_name = "company2",
            short_name="lmao",
            email= "company2@gmail.com",
            phone= "1987654321"
        )

        admin_user = User.objects.create_user(
            username="admin1",
            password="123456",
            email="admin1@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        admin = Administrator.objects.create(
            user=admin_user,
            user_type="A",
            identifier="adm01",
            phone="666555444",
            company_id=company1
        )

        employee1_user = User.objects.create_user(
            username="emp1",
            password="123456",
            email="emp1@metronus.es",
            first_name="Álvaro",
            last_name="Varo"
        )

        employee2_user = User.objects.create_user(
            username="emp2",
            password="123456",
            email="emp2@metronus.es",
            first_name="Alberto",
            last_name="Berto"
        )

        employee1 = Employee.objects.create(
            user=employee1_user,
            user_type="E",
            identifier="emp01",
            phone="666555444",
            company_id=company1
        )

        employee2 = Employee.objects.create(
            user=employee2_user,
            user_type="E",
            identifier="emp02",
            phone="666555444",
            company_id=company2
        )
        dep1=Department.objects.create(name="dep1",active=True,company_id=company1)
        dep2=Department.objects.create(name="dep2",active=True,company_id=company1)
        dep3=Department.objects.create(name="dep3",active=False,company_id=company1)
        dep4=Department.objects.create(name="dep3",active=True,company_id=company2)
        
        proj1=Project.objects.create(name="TestProject",deleted=False,company_id=company1)
        Project.objects.create(name="TestProject2",deleted=False,company_id=company1)
        pd1 = ProjectDepartment.objects.create(
            project_id = proj1,
            department_id = dep1)
        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd1,
            employee_id=employee1,
            role_id= Role.objects.create(name="Project manager", tier=40))
    def test_create_department_positive(self):
        # Logged in as an administrator, try to create an department
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = Department.objects.all().count()

        response = c.post("/department/create", {
            "department_id": "0",
            "name": "dep4",
        })

        self.assertEquals(response.status_code, 302)

        # Check that the department has been successfully created

        dep = Department.objects.all().last()
        self.assertEquals(dep.name, "dep4")
        self.assertEquals(dep.company_id,Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(dep.active,True)
        logs_after = Department.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_async_department_positive(self):
        # Logged in as an administrator, try to create an department
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = Department.objects.all().count()

        response = c.post("/department/createAsync", {
            "department_id": "0",
            "name": "dep4",
        })

        self.assertEquals(response.status_code, 200)

        # Check that the department has been successfully created

        dep = Department.objects.all().last()
        self.assertEquals(dep.name, "dep4")
        self.assertEquals(dep.company_id,Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(dep.active,True)

        #response in bytes must be decode to string
        data=response.content.decode("utf-8")
        #string to dict
        data=json.loads(data)
        self.assertEquals(data["repeated_name"],False)
        self.assertEquals(data["success"],True)
        logs_after = Department.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)


    def test_create_department_duplicate(self):
        # Logged in as an administrator, try to create an department with the name of an existing company
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = Department.objects.all().count()

        response = c.post("/department/create", {
            "department_id": "0",
            "name": "dep1",
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["repeated_name"],True)


    def test_create_department_not_logged(self):
        c = Client()
        response = c.get("/department/create")
        self.assertEquals(response.status_code, 403)

    def test_create_department_not_allowed(self):
        c = Client()
        c.login(username="emp2", password="123456")
        response = c.get("/department/create")
        self.assertEquals(response.status_code, 403)

    def test_list_departments_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["departments"]), 2)
        self.assertEquals(response.context["departments"][0].name, "dep1")


    def test_list_departments_positive_2(self):
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/department/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["departments"]), 1)
        self.assertEquals(response.context["departments"][0].name, "dep1")

    def test_view_department_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        dep_id=response.context["departments"][0].id
        response = c.get("/department/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["employees"]), 1)
        self.assertEquals(len(response.context["tasks"]), 0)
        #self.assertEquals(response.context["employees"][0].department.id, dep_id)
        self.assertEquals(response.context["coordinator"],None)
    def test_view_department_not_allowed(self):
        c = Client()
        c.login(username="emp2", password="123456")
        dep_id=Department.objects.all().first()
        response = c.get("/department/view/"+str(dep_id.id)+"/")
        self.assertEquals(response.status_code, 403)


    def test_list_departments_not_logged(self):
        c = Client()
        response = c.get("/department/list")
        self.assertEquals(response.status_code, 403)

    def test_list_departments_not_allowed(self):
        c = Client()
        c.login(username="emp2", password="123456")
        response = c.get("/department/list")
        self.assertEquals(response.status_code, 403)


    def test_edit_department_get(self):
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/department/list")
        dep_id=response.context["departments"][0].id
        response = c.get("/department/edit/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["name"], "dep1")
        self.assertEquals(form.initial["department_id"], dep_id)

    def test_edit_department_404(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/edit?department_id=9000")
        self.assertEquals(response.status_code, 404)


    def test_delete_department_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        dep_id=response.context["departments"][0].id

        response = c.get("/department/delete/"+str(dep_id)+"/")
        self.assertRedirects(response, "/department/list", fetch_redirect_response=False)

        self.assertFalse(Department.objects.get(pk=dep_id).active)

    def test_delete_department_not_allowed(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        dep_id=response.context["departments"][0].id
        c.logout()
        c.login(username="admin2", password="123456")
        response = c.get("/department/delete/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_delete_department_not_active(self):
        c = Client()
        c.login(username="admin1", password="123456")

        dep_id=Department.objects.get(active=False).id
        response = c.get("/department/delete/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 403)
