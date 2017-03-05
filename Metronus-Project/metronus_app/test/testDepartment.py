from metronus_app.model.department import Department
import metronus_app.view.departmentView

from django.test import TestCase

class DepartmentTestCase(TestCase):
    def setUp(self):
        Company.objects.create(
            cif="123",
            name = "company1",
            email= "company1@gmail.com",
            phone= "123456789",
            pswd= "algo")
        Company.objects.create(
            cif="124",
            name = "company2",
            email= "company2@gmail.com",
            phone= "987654321",
            pswd= "algomas")

    def test_create_department(self):
        company=Company.objects.get(name="124")
        Department.objects.create(name="dep1",active=True,company_id=company.id)

    def test_update_department(self):
        dep=Department.objects.get(name="dep1")
        dep['name']="dep1new"
        dep.save()
    def test_delete_department(self):
        dep=Department.objects.get(name="dep1")
        deleteDepartment(department)

    def test_check_valid_company_department(self):
        company=Company.objects.get(name="124")
        checkCompanyDepartment(department,company.id)
