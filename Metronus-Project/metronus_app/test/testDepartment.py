from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.contrib.auth.models import User
from metronus_app.model.administrator import Administrator
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.test import TestCase, Client
from django.urls import reverse
import json


class DepartmentTestCase(TestCase):
    """This class provides a test case for department management"""
    @classmethod
    def setUpTestData(cls):
        """
        Loads the data to the database for tests to be done
        """
        company1 = Company.objects.create(
            cif="123",
            company_name="company1",
            short_name="mplp",
            email="company1@gmail.com",
            phone="123456789"
        )

        company2 = Company.objects.create(
            cif="456",
            company_name="company2",
            short_name="lmao",
            email="company2@gmail.com",
            phone="1987654321"
        )

        admin_user = User.objects.create_user(
            username="admin1",
            password="123456",
            email="admin1@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        # Admin
        Administrator.objects.create(
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

        # Employee 1
        employee1 = Employee.objects.create(
            user=employee1_user,
            user_type="E",
            identifier="emp01",
            phone="666555444",
            company_id=company1
        )

        # Employee 2
        Employee.objects.create(
            user=employee2_user,
            user_type="E",
            identifier="emp02",
            phone="666555444",
            company_id=company2
        )
        dep1 = Department.objects.create(name="dep1", active=True, company_id=company1)
        Department.objects.create(name="dep2", active=True, company_id=company1)
        Department.objects.create(name="dep3", active=False, company_id=company1)
        Department.objects.create(name="dep3", active=True, company_id=company2)

        proj1 = Project.objects.create(name="TestProject", deleted=False, company_id=company1)
        Project.objects.create(name="TestProject2", deleted=False, company_id=company1)
        pd1 = ProjectDepartment.objects.create(
            project_id=proj1,
            department_id=dep1)
        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd1,
            employee_id=employee1,
            role_id=Role.objects.create(name="Project manager", tier=40))

    def test_create_department_positive(self):
        """ Logged in as an administrator, try to create an department"""
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
        self.assertEquals(dep.company_id, Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(dep.active, True)
        logs_after = Department.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_async_department_positive(self):
        """ Logged in as an administrator, try to create an department"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = Department.objects.all().count()

        response = c.post(reverse("department_create_async"), {
            "department_id": "0",
            "name": "dep4",
        })

        self.assertEquals(response.status_code, 200)

        # Check that the department has been successfully created

        dep = Department.objects.all().last()
        self.assertEquals(dep.name, "dep4")
        self.assertEquals(dep.company_id, Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(dep.active, True)

        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)
        self.assertEquals(data["repeated_name"], False)
        self.assertEquals(data["success"], True)
        logs_after = Department.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)
    def test_create_department_duplicate_async(self):
        """ Logged in as an administrator, try to create an department with the name of an existing company"""
        c = Client()
        c.login(username="admin1", password="123456")

        # ??????????????????? Again
        # logs_before = Department.objects.all().count()

        response = c.post(reverse("department_create_async"), {
            "department_id": "0",
            "name": "dep1",
        })

        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)
        self.assertEquals(data["repeated_name"], True)
        self.assertEquals(data["success"], False)

    def test_create_department_duplicate(self):
        """ Logged in as an administrator, try to create an department with the name of an existing company"""
        c = Client()
        c.login(username="admin1", password="123456")

        # ??????????????????? Again
        # logs_before = Department.objects.all().count()

        response = c.post("/department/create", {
            "department_id": "0",
            "name": "dep1",
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["repeated_name"], True)

    def test_create_department_not_logged(self):
        """ Without authentication, try to create an department """
        c = Client()
        response = c.get("/department/create")
        self.assertEquals(response.status_code, 403)

    def test_create_department_not_allowed(self):
        """ Without proper roles, try to create an department """
        c = Client()
        c.login(username="emp2", password="123456")
        response = c.get("/department/create")
        self.assertEquals(response.status_code, 403)

    def test_list_departments_positive(self):
        """As an admin, try to list the departments """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["departments"]), 2)
        self.assertEquals(response.context["departments"][0].name, "dep1")

    def test_list_departments_positive_2(self):
        """As an employee with proper roles, try to list the departments """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/department/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["departments"]), 1)
        self.assertEquals(response.context["departments"][0].name, "dep1")

    def test_view_department_positive(self):
        """As an admin, try to view a department """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        department=response.context["departments"][0]
        dep_id = department.id
        response = c.get("/department/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["employees"]), 
            Employee.objects.filter(user__is_active=True,
            projectdepartmentemployeerole__projectDepartment_id__department_id=department,
            projectdepartmentemployeerole__role_id__tier__lte=20).distinct().count())

        

        self.assertEquals(len(response.context["tasks"]), 0)
        # self.assertEquals(response.context["employees"][0].department.id, dep_id)
        self.assertTrue(response.context["coordinators"] is not None)

    def test_view_department_not_allowed(self):
        """Without proper roles, try to view a department """
        c = Client()
        c.login(username="emp2", password="123456")
        dep_id = Department.objects.all().first()
        response = c.get("/department/view/"+str(dep_id.id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_list_departments_not_logged(self):
        """Without authentication, try to list the departments """
        c = Client()
        response = c.get("/department/list")
        self.assertEquals(response.status_code, 403)

    def test_list_departments_not_allowed(self):
        """Without proper roles, try to list the departments """
        c = Client()
        c.login(username="emp2", password="123456")
        response = c.get("/department/list")
        self.assertEquals(response.status_code, 403)

    def test_edit_department_get(self):
        """As an admin, try to get the edit department form """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/department/list")
        dep_id = response.context["departments"][0].id
        response = c.get("/department/edit/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["name"], "dep1")
        self.assertEquals(form.initial["department_id"], dep_id)

    def test_edit_department_404(self):
        """As an admin, try to edit an inexistent department"""
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/edit?department_id=9000")
        self.assertEquals(response.status_code, 404)

    def test_edit_department_positive(self):
            """
            Logged in as an administrator, try to edit a deapartment
            """
            c = Client()
            c.login(username="admin1", password="123456")

            pro=Department.objects.get(name="dep1")

            response = c.post("/department/edit/"+str(pro.id)+"/", {
                "department_id": pro.id,
                "name": "Metronosa"
                  })

            self.assertEquals(response.status_code, 302)

            pro_up=Department.objects.get(pk=pro.id)

            self.assertEquals(pro_up.name, "Metronosa")

    def test_delete_department_positive(self):
        """As an admin, try to delete a department"""
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        dep_id = response.context["departments"][0].id

        response = c.get("/department/delete/"+str(dep_id)+"/")
        self.assertRedirects(response, "/department/list", fetch_redirect_response=False)

        self.assertFalse(Department.objects.get(pk=dep_id).active)

    def test_delete_department_not_allowed(self):
        """As an admin, try to delete a department from other company"""
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        dep_id = response.context["departments"][0].id
        c.logout()
        c.login(username="admin2", password="123456")
        response = c.get("/department/delete/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_delete_department_not_active(self):
        """As an admin, try to delete an already deleted department """
        c = Client()
        c.login(username="admin1", password="123456")

        dep_id = Department.objects.get(active=False).id
        response = c.get("/department/delete/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 404)

    def test_recover_department_positive(self):
        """As an admin, recover a department"""
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/department/list")
        dep_id = Department.objects.get(active=False).id

        response = c.get(reverse("department_recover",args=(dep_id,)))
        self.assertRedirects(response, "/department/list", fetch_redirect_response=False)

        self.assertTrue(Department.objects.get(pk=dep_id).active)
