from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.model.department import Department
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.controllers.projectDepartmentController import *

from django.test import TestCase

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

		proj1 = Project.objects.create(name="TestProject",deleted=False,company_id=company124)
		proj2 = Project.objects.create(name="TestProject2",deleted=False,company_id=company124)
		dep1 = Department.objects.create(name="Departamento1",active=True,company_id=company124)
		dep2 = Department.objects.create(name="Departamento2",active=True,company_id=company124)
		pd = ProjectDepartment.objects.create(project_id = proj1, department_id = dep2)
		print(pd)
	

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

