from metronus_app.model.department import Department
from metronus_app.model.company import Company
from metronus_app.controllers.departmentController import *

from django.test import TestCase

class DepartmentTestCase(TestCase):
    def setUp(self):
        Company.objects.create(
            cif="123",
            company_name = "company1",
            short_name="cosa",
            email= "company1@gmail.com",
            phone= "123456789")
        Company.objects.create(
            cif="124",
            company_name="company2",
            short_name="cosa",
            email= "company2@gmail.com",
            phone= "987654321")
        company=Company.objects.get(cif="124")
        Department.objects.create(name="dep3",active=True,company_id=company)


    def test_create_department(self):
        """
        checks the number of departments increased
        """
        cuenta=Department.objects.count()
        company=Company.objects.get(cif="124")
        Department.objects.create(name="dep1",active=True,company_id=company)
        cuenta2=Department.objects.count()
        self.assertTrue(cuenta+1,cuenta2)

    def test_update_department(self):
        dep=Department.objects.get(name="dep3")
        dep.name="dep1new"
        dep.save()


    def test_delete_department(self):
        """
        checks the number of active departments increased
        """
        company=Company.objects.get(cif="124")
        cuenta=Department.objects.filter(company_id=company,active=True).count()
        dep=Department.objects.get(name="dep3")
        deleteDepartment(dep)
        cuenta2=Department.objects.filter(company_id=company,active=True).count()
        self.assertEqual(cuenta,cuenta2+1)

    def test_list_department(self):
        """
        checks the number of departments
        """
        company=Company.objects.get(cif="124")
        lista=Department.objects.filter(company_id=company,active=True)
        self.assertEqual(lista.count(),1)

    def test_check_valid_company_department(self):
        """
        checks the company is valid
        """
        department=Department.objects.get(name="dep3")
        company=Company.objects.get(cif="124")
        self.assertTrue(checkCompanyDepartment(department,company.id))

    def test_check_valid_company_departmentId(self):
        """
        checks the company is valid given a department id
        """
        department=Department.objects.get(name="dep3")
        company=Company.objects.get(cif="124")
        self.assertTrue(checkCompanyDepartmentId(department.id,company.id))

    def test_check_valid_company_department(self):
        """
        checks the company is NOT valid
        """
        department=Department.objects.get(name="dep3")
        company=Company.objects.get(cif="123")
        self.assertFalse(checkCompanyDepartment(department,company.id))
