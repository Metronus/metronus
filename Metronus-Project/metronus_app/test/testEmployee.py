from django.test                                 import TestCase, Client

from metronus_app.controllers.employeeController import create

from metronus_app.model.company                  import Company
from metronus_app.model.employee                 import Employee
from metronus_app.model.administrator            import Administrator
from django.contrib.auth.models                  import User

class EmployeeTestCase(TestCase):

    def setUp(self):
        company = Company.objects.create(
            cif="123",
            company_name = "company1",
            short_name="mplp",
            email= "company1@gmail.com",
            phone= "123456789"
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
            company_id=company
        )

    def test_create_employee_positive(self):
        # Logged in as an administrator, try to create an employee
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.post("/en/employee/create", {
            "username": "employee1",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
        })

        self.assertEquals(response.status_code, 200)

        # Check that the employee has been successfully created

        employee = Employee.objects.get(identifier="frc01")
        self.assertEquals(employee.user_type, "E")
        self.assertEquals(employee.phone, "654321987")
        self.assertEquals(employee.company_id, Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(employee.user.username, "employee1")
        self.assertEquals(employee.user.first_name, "Francisco")
        self.assertEquals(employee.user.last_name, "Romualdo")
        self.assertEquals(employee.user.email, "frc@empresa.com")
