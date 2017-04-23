from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from django.test import TestCase, Client
from metronus_app.model.employee import Employee
from django.core.exceptions import PermissionDenied
from metronus_app.controllers.projectController import check_company_project


class ProjectTestCase(TestCase):
    """This class provides a test case for project management"""
    def setUp(self):
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
        Employee.objects.create(
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

        Project.objects.create(name="pro1", deleted=False, company_id=company1)
        Project.objects.create(name="pro2", deleted=False, company_id=company1)
        Project.objects.create(name="pro3", deleted=True, company_id=company1)
        Project.objects.create(name="pro3", deleted=False, company_id=company2)

    def test_create_project_positive(self):
        """
        Logged in as an administrator, try to create a project
        """
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = Project.objects.all().count()

        response = c.post("/project/create", {
            "project_id": "0",
            "name": "pro4",
        })

        self.assertEquals(response.status_code, 302)

        # Check that the department has been successfully created

        pro = Project.objects.all().last()
        self.assertEquals(pro.name, "pro4")
        self.assertEquals(pro.company_id, Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(pro.deleted, False)
        logs_after = Project.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_project_duplicate(self):
        """ Logged in as an administrator, try to create a project with the name of an existing company """
        c = Client()
        c.login(username="admin1", password="123456")

        # ??????????????????????????????????????
        # logs_before = Project.objects.all().count()

        response = c.post("/project/create", {
            "project_id": "0",
            "name": "pro1",
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["repeated_name"], True)

    def test_create_project_not_logged(self):
        """ Without authentication, try to create a project """
        c = Client()
        response = c.get("/project/create")
        self.assertEquals(response.status_code, 403)

    def test_create_project_not_allowed(self):
        """ Without proper roles, try to create a project """
        c = Client()
        c.login(username="emp1", password="123456")
        response = c.get("/project/create")
        self.assertEquals(response.status_code, 403)

    def test_list_projects_positive(self):
        """ List the projects as an admin """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/project/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["projects"]), 2)
        self.assertEquals(response.context["projects"][0].name, "pro1")

    def test_list_projects_not_logged(self):
        """ List the projects without authentication """
        c = Client()
        response = c.get("/project/list")
        self.assertEquals(response.status_code, 403)

    def test_list_projects_not_allowed(self):
        """ List the projects without proper roles """
        c = Client()
        c.login(username="emp1", password="123456")
        response = c.get("/project/list")
        self.assertEquals(response.status_code, 403)

    def test_edit_project_get(self):
        """ Get the edit project form as an admin """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/project/list")
        pro_id = response.context["projects"][0].id
        response = c.get("/project/edit/" + str(pro_id) + "/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["name"], "pro1")
        self.assertEquals(form.initial["project_id"], pro_id)

    def test_edit_project_404(self):
        """ Try getting the edit project form as an admin from other company """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/project/edit/9000/")
        self.assertEquals(response.status_code, 404)

    def test_delete_project_positive(self):
        """
        As an admin, delete a project
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/project/list")
        pro_id = response.context["projects"][0].id
        response = c.get("/project/delete/" + str(pro_id) + "/")
        self.assertRedirects(response, "/project/list", fetch_redirect_response=False)

        self.assertTrue(Project.objects.get(pk=pro_id).deleted)

    def test_delete_project_not_allowed(self):
        """
        As an admin, delete a project from other company
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/project/list")
        pro_id = response.context["projects"][0].id
        c.logout()
        c.login(username="admin2", password="123456")
        response = c.get("/project/delete/" + str(pro_id) + "/")
        self.assertEquals(response.status_code, 403)

    def test_delete_project_not_active(self):
        """
        As an admin, delete an already deleted project
        """
        c = Client()
        c.login(username="admin1", password="123456")

        pro_id = Project.objects.get(deleted=True).id
        response = c.get("/project/delete/" + str(pro_id) + "/")
        self.assertEquals(response.status_code, 403)

    def test_check_valid_company_project(self):
        """
        checks the company is valid
        """
        project = Project.objects.get(name="pro1")
        company = Company.objects.get(cif="123")
        self.assertTrue(check_company_project(project, company))

    def test_check_not_valid_company_project(self):
        """
        checks the company is NOT valid
        """
        project = Project.objects.get(name="pro1")
        company = Company.objects.get(cif="456")
        self.assertRaises(PermissionDenied, check_company_project, project, company)
