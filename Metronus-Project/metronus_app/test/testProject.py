from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.controllers.projectController import *

from django.test import TestCase

class ProjectTestCase(TestCase):
	def setUp(self):
		Company.objects.create(
			cif="123",
			company_name="company1",
			short_name="cosa",
			email="company1@gmail.com",
			phone="123456789")
		Company.objects.create(
			cif="124",
			company_name="company2",
			short_name="cosa",
			email="company2@gmail.com",
			phone="987654321")
		company=Company.objects.get(cif="124")
		Project.objects.create(name="TestProject",deleted=False,company_id=company)
	

	def test_create_project(self):
		"""
		#checks the number of projects increased
		"""
		cuenta=Project.objects.count()
		company=Company.objects.get(cif="124")
		Project.objects.create(name="Project",deleted=False,company_id=company)
		cuenta2=Project.objects.count()
		self.assertTrue(cuenta+1,cuenta2)

	def test_update_project(self):
		projct=Project.objects.get(name="TestProject")
		projct.name="Project_Edited"
		projct.save()


	def test_delete_project(self):
		"""
		#checks the number of active projects increased
		"""
		company=Company.objects.get(cif="124")
		cuenta=Project.objects.filter(company_id=company,deleted=False).count()
		projct=Project.objects.get(name="TestProject")
		deleteProject(projct)
		cuenta2=Project.objects.filter(company_id=company,deleted=False).count()
		self.assertEqual(cuenta,cuenta2+1)

	def test_list_project(self):
		"""
		#checks the number of projects
		"""
		company=Company.objects.get(cif="124")
		lista=Project.objects.filter(company_id=company,deleted=False)
		self.assertEqual(lista.count(),1)

	def test_check_valid_company_project(self):
		"""
		#checks the company is valid
		"""
		project=Project.objects.get(name="TestProject")
		company=Company.objects.get(cif="124")
		self.assertTrue(checkCompanyProject(project,company.id))

	def test_check_valid_company_project(self):
		"""
		#checks the company is NOT valid
		"""
		project=Project.objects.get(name="TestProject")
		company=Company.objects.get(cif="123")
	