from django.test                                 import TestCase, Client

from metronus_app.model.company                  import Company
from metronus_app.model.employee                 import Employee
from metronus_app.model.administrator            import Administrator
from django.contrib.auth.models                  import User
from metronus_app.model.employeeLog              import EmployeeLog

class EmployeeTestCase(TestCase):

    def setUp(self):
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

    def test_create_employee_positive(self):
        # Logged in as an administrator, try to create an employee
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

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

        logs_after = EmployeeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)


    def test_list_employees_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/en/employee/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["employees"]), 1)
        self.assertEquals(response.context["employees"][0].identifier, "emp01")

    def test_list_employees_not_logged(self):
        c = Client()
        response = c.get("/en/employee/list")
        self.assertEquals(response.status_code, 403)

    def test_view_employee_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/en/employee/view/emp1/")

        self.assertEquals(response.status_code, 200)
        employee = response.context["employee"]
        self.assertTrue(employee)
        self.assertEquals(employee.identifier, "emp01")
        self.assertEquals(employee.user.first_name, "Álvaro")

    def test_view_employee_not_allowed(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/en/employee/view/emp2/")
        self.assertEquals(response.status_code, 403)

    def test_view_employee_404(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/en/employee/view/marta/")
        self.assertEquals(response.status_code, 404)

    def test_edit_employee_get(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/en/employee/edit/emp1/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["first_name"], "Álvaro")
        self.assertEquals(form.initial["last_name"], "Varo")
        self.assertEquals(form.initial["email"], "emp1@metronus.es")
        self.assertEquals(form.initial["identifier"], "emp01")
        self.assertEquals(form.initial["phone"], "666555444")

    def test_edit_employee_positive_without_pass(self):
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="emp1").password

        response = c.post("/en/employee/edit/emp1/", {
            "password1": "",
            "password2": "",
            "first_name": "NuevoNombre",
            "last_name": "NuevoApellido",
            "email": "nuevocorreo@empresa.com",
            "identifier": "nuevoid",
            "phone": "nuevotelefono",
        })

        self.assertRedirects(response, "/employee/view/emp1/", fetch_redirect_response=False)

        final = Employee.objects.get(user__username="emp1")
        self.assertEquals(final.identifier, "nuevoid")
        self.assertEquals(final.phone, "nuevotelefono")
        self.assertEquals(final.user.first_name, "NuevoNombre")
        self.assertEquals(final.user.last_name, "NuevoApellido")
        self.assertEquals(final.user.email, "nuevocorreo@empresa.com")
        self.assertEquals(final.user.password, initialpass)

    def test_edit_employee_positive_with_pass(self):
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="emp1").password

        response = c.post("/en/employee/edit/emp1/", {
            "password1": "nuevapassword",
            "password2": "nuevapassword",
            "first_name": "NuevoNombre2",
            "last_name": "NuevoApellido2",
            "email": "nuevocorreo2@empresa.com",
            "identifier": "nuevoid2",
            "phone": "nuevotelefono2",
        })

        self.assertRedirects(response, "/employee/view/emp1/", fetch_redirect_response=False)

        final = Employee.objects.get(user__username="emp1")
        self.assertEquals(final.identifier, "nuevoid2")
        self.assertEquals(final.phone, "nuevotelefono2")
        self.assertEquals(final.user.first_name, "NuevoNombre2")
        self.assertEquals(final.user.last_name, "NuevoApellido2")
        self.assertEquals(final.user.email, "nuevocorreo2@empresa.com")
        self.assertTrue(final.user.password != initialpass)

    def test_edit_employee_not_allowed(self):
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/en/employee/edit/emp2/")
        self.assertEquals(response.status_code, 403)

    def test_edit_employee_404(self):
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/en/employee/edit/diana/")
        self.assertEquals(response.status_code, 404)

    def test_delete_employee_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()
        self.assertTrue(User.objects.get(username="emp1").is_active)

        response = c.get("/en/employee/delete/emp1/")
        self.assertRedirects(response, "/employee/list/", fetch_redirect_response=False)

        self.assertFalse(User.objects.get(username="emp1").is_active)
        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before + 1, logs_after)