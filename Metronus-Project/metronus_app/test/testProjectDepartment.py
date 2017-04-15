from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models	import User
from django.test import TestCase, Client


class ProjectDepartmentTestCase(TestCase):
    """This class provides a test case for using and managing project-departement relationship"""
    def setUp(self):

        company123 = Company.objects.create(
            cif="123",
            company_name="company1",
            short_name="shorty1",
            email="company1@gmail.com",
            phone="123456789")

        company124 = Company.objects.create(
            cif="124",
            company_name="company2",
            short_name="shorty2",
            email="company2@gmail.com",
            phone="987654321")

        admin_user1 = User.objects.create_user(
            username="admin",
            password="1234",
            email="admin@metronus.es",
            first_name="Admin",
            last_name="Istrator")

        admin_user2 = User.objects.create_user(
            username="admin2",
            password="4321",
            email="admin2@metronus.es",
            first_name="Nimad",
            last_name="Rotartis")

        admin1 = Administrator.objects.create(
            user=admin_user1,
            user_type="A",
            identifier="adm01",
            phone="999999999",
            company_id=company124)

        admin2 = Administrator.objects.create(
            user=admin_user2,
            user_type="A",
            identifier="adm02",
            phone="666666666",
            company_id=company123)

        proj1 = Project.objects.create(
            name="TestProject",
            deleted=False,
            company_id=company124)

        proj2 = Project.objects.create(
            name="TestProject2",
            deleted=False,
            company_id=company124)

        proj3 = Project.objects.create(
            name="TestProjectC2",
            deleted=False,
            company_id=company123)

        proj4 = Project.objects.create(
            name="TestProjectDeleted",
            deleted=True,
            company_id=company124)

        dep1 = Department.objects.create(
            name="Departamento1",
            active=True,company_id=company124)

        dep2 = Department.objects.create(
            name="Departamento2",
            active=True,
            company_id=company124)

        dep3 = Department.objects.create(
            name="DepartamentoC2",
            active=True,
            company_id=company123)

        dep3 = Department.objects.create(
            name="DepartamentoInactivo",
            active=False,
            company_id=company124)

        pd = ProjectDepartment.objects.create(
            project_id = proj1,
            department_id = dep2)

        pd = ProjectDepartment.objects.create(
            project_id = proj1,
            department_id = dep1)

    #---------------------- CREATE

    def test_create_project_department_positive(self):
        """
		#checks the number of projectDepartments increased
		"""
        c = Client()
        c.login(username="admin", password="1234")

        project = Project.objects.get(name="TestProject2")
        department = Department.objects.get(name="Departamento1")
        count=ProjectDepartment.objects.all().count()

        response = c.post("/projectdepartment/create", {
            "projectDepartment_id": "0",
            "project_id": project.id,
            "department_id": department.id,
        })

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(count + 1, count2)


    def test_create_project_department_negative_project(self):
        """
		#checks the number of projectDepartments didn't increase
		Admin is trying to create a projectDepartment using a project that's not from his Company
		"""
        c = Client()
        c.login(username="admin", password="1234")

        project = Project.objects.get(name="TestProjectC2")
        department = Department.objects.get(name="Departamento1")
        count=ProjectDepartment.objects.all().count()

        response = c.post("/projectdepartment/create", {
            "projectDepartment_id": "0",
            "project_id": project.id,
            "department_id": department.id,
        })

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(count, count2)


    def test_create_project_department_negative_project2(self):
        """
		#checks the number of projectDepartments didn't increase
		Admin is trying to create a projectDepartment using a project that's deleted
		"""
        c = Client()
        c.login(username="admin", password="1234")

        project = Project.objects.get(name="TestProjectDeleted")
        department = Department.objects.get(name="Departamento1")
        count=ProjectDepartment.objects.all().count()

        response = c.post("/projectdepartment/create", {
            "projectDepartment_id": "0",
            "project_id": project.id,
            "department_id": department.id,
        })

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(count, count2)


    def test_create_project_department_negative_department1(self):
        """
		#checks the number of projectDepartments didn't increase
		Admin is trying to create a projectDepartment using a department that's not from his Company
		"""
        c = Client()
        c.login(username="admin", password="1234")

        project = Project.objects.get(name="TestProject2")
        department = Department.objects.get(name="DepartamentoC2")
        count=ProjectDepartment.objects.all().count()

        response = c.post("/projectdepartment/create", {
            "projectDepartment_id": "0",
            "project_id": project.id,
            "department_id": department.id,
        })

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(count, count2)


    def test_create_project_department_negative_department2(self):
        """
		#checks the number of projectDepartments didn't increase
		Admin is trying to create a projectDepartment using a department that's not active
		"""
        c = Client()
        c.login(username="admin", password="1234")

        project = Project.objects.get(name="TestProject2")
        department = Department.objects.get(name="DepartamentoInactivo")
        count=ProjectDepartment.objects.all().count()

        response = c.post("/projectdepartment/create", {
            "projectDepartment_id": "0",
            "project_id": project.id,
            "department_id": department.id,
        })

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(count, count2)

    #---------------------- LIST

    def test_list_admin1_positive(self):
        #Logged as admin1, his company has 2 projectDepartments
        c = Client()
        c.login(username="admin", password="1234")

        response = c.get("/projectdepartment/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["projectDepartments"]), 2)


    def test_list_admin1_dep1_positive(self):
        #Logged as admin1, list the projectDepartments of Departamento1
        c = Client()
        c.login(username="admin", password="1234")

        dep = Department.objects.get(name="Departamento1")
        response = c.get("/projectdepartment/list", {"department_id" : dep.id})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["projectDepartments"]), 1)


    def test_list_admin1_proj2_positive(self):
        #Logged as admin1, list the projectDepartments of TestProject2
        c = Client()
        c.login(username="admin", password="1234")

        proj = Project.objects.get(name="TestProject2")
        response = c.get("/projectdepartment/list", {"project_id" : proj.id})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["projectDepartments"]), 0)


    def test_list_admin2_positive(self):
        #Logged as admin2, his company has 0 projectDepartments
        c = Client()
        c.login(username="admin2", password="4321")

        response = c.get("/projectdepartment/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["projectDepartments"]), 0)


    #---------------------- DELETE

    def test_delete_positive(self):
        #Logged as admin, tries to delete a PD that belongs to his company
        c = Client()
        c.login(username="admin", password="1234")

        project = Project.objects.get(name="TestProject")
        department = Department.objects.get(name="Departamento1")
        pd = ProjectDepartment.objects.get(project_id = project, department_id = department)
        count=ProjectDepartment.objects.all().count()

        response = c.get("/projectdepartment/delete", {"projectDepartment_id" : pd.id})

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(response.status_code, 302)
        self.assertEquals(count - 1, count2)

    def test_delete_negative(self):
        #Logged as admin2, tries to delete a PD that's not from his company
        c = Client()
        c.login(username="admin2", password="4321")

        project = Project.objects.get(name="TestProject")
        department = Department.objects.get(name="Departamento1")
        pd = ProjectDepartment.objects.get(project_id = project, department_id = department)
        count=ProjectDepartment.objects.all().count()

        response = c.get("/projectdepartment/delete", {"projectDepartment_id" : pd.id})

        count2=ProjectDepartment.objects.all().count()

        self.assertEquals(count, count2)
        self.assertEquals(response.status_code, 403)
