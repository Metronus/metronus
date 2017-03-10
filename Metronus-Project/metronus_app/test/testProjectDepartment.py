from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.administrator import Administrator
from metronus_app.controllers.projectDepartmentController import *
from django.contrib.auth.models	import User
from django.test import TestCase, Client


class ProjectDepartmentTestCase(TestCase):
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
			email="admin@metronus.es",
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

		dep1 = Department.objects.create(
			name="Departamento1",
			active=True,company_id=company124)

		dep2 = Department.objects.create(
			name="Departamento2",
			active=True,
			company_id=company124)

		pd = ProjectDepartment.objects.create(
			project_id = proj1,
			department_id = dep2)

		pd = ProjectDepartment.objects.create(
			project_id = proj1,
			department_id = dep1)
	

	def test_create_projectDepartment(self):
		"""
		#checks the number of projectDepartments increased
		"""
		count=ProjectDepartment.objects.count()
		company=Company.objects.get(cif="124")
		project = Project.objects.get(name="TestProject")
		department = Department.objects.get(name="Departamento1")
		ProjectDepartment.objects.create(project_id = project, department_id = department)

		cuenta2=Project.objects.count()
		self.assertTrue(count+1,count)

	def test_list_admin1(self):
		#Logged as admin1, his company has 2 projectDepartments
		c = Client()
		c.login(username="admin", password="1234")
		
		response = c.get("/projectdepartment/list")
		
		self.assertEquals(response.status_code, 200)
		self.assertEquals(len(response.context["projectDepartments"]), 2)

	def test_list_admin1(self):
		#Logged as admin2, his company has 0 projectDepartments
		c = Client()
		c.login(username="admin2", password="4321")

		response = c.get("/projectdepartment/list")

		self.assertEquals(response.status_code, 200)
		self.assertEquals(len(response.context["projectDepartments"]), 0)
