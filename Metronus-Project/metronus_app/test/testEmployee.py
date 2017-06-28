from django.test import TestCase, Client

from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from metronus_app.model.employeeLog import EmployeeLog
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
from metronus_app.model.role                          import Role
from metronus_app.model.projectDepartment             import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.urls import reverse
from populate_database                  import populate_roles
import json

class EmployeeTestCase(TestCase):
    """This class provides a test case for employee management"""
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
        employee3_user = User.objects.create_user(
            username="emp3",
            password="123456",
            email="emp3@metronus.es",
            first_name="Alberto",
            last_name="Bertoa"
        )

        # Employee 1
        emp1=Employee.objects.create(
            user=employee1_user,
            user_type="E",
            identifier="emp01",
            phone="666555444",
            company_id=company1
        )
        # Employee 3
        emp2=Employee.objects.create(
            user=employee3_user,
            user_type="E",
            identifier="emp03",
            phone="666553444",
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

        proj1 = Project.objects.create(
            name="Metronus",
            deleted=False,
            company_id=company1)

        dep1 = Department.objects.create(
            name="Backend",
            active=True,company_id=company1)

        dep2 = Department.objects.create(
            name="Frontend",
            active=True,
            company_id=company1)

        #Frontend
        pd1 = ProjectDepartment.objects.create(
            project_id = proj1,
            department_id = dep1)

        #Backend
        pd2 = ProjectDepartment.objects.create(
            project_id = proj1,
            department_id = dep2)

        populate_roles()

        emp_role=Role.objects.get(name="EMPLOYEE")
        coor_role=Role.objects.get(name="COORDINATOR")
        pm_role=Role.objects.get(name="PROJECT_MANAGER")
        team_role=Role.objects.get(name="TEAM_MANAGER")

        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd1,
            employee_id=emp1,
            role_id= emp_role)
        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd1,
            employee_id=emp2,
            role_id=pm_role)

    def test_create_form_view(self):
        """ Logged in as an administrator, get the form view"""
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.post("/employee/create")

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context["form"] is not None)

    def test_create_employee_positive(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create", {
            "username": "employee1",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "1.0"
        })

        self.assertRedirects(response, "/employee/view/employee1/", fetch_redirect_response=False)

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

    def test_create_employee_with_redirect_positive(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create?redirect=true", {
            "username": "employee11343154",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "Francisco2",
            "last_name": "Romualdo2",
            "email": "frc2@empresa.com",
            "identifier": "frc02",
            "phone": "654321987",
            "price_per_hour": "2.0"
        })

        self.assertRedirects(response, "/employee/view/employee11343154/", fetch_redirect_response=False)

        # Check that the employee has been successfully created

        employee = Employee.objects.get(identifier="frc02")
        self.assertEquals(employee.user_type, "E")
        self.assertEquals(employee.phone, "654321987")
        self.assertEquals(employee.company_id, Administrator.objects.get(identifier="adm01").company_id)
        self.assertEquals(employee.user.username, "employee11343154")
        self.assertEquals(employee.user.first_name, "Francisco2")
        self.assertEquals(employee.user.last_name, "Romualdo2")
        self.assertEquals(employee.user.email, "frc2@empresa.com")

        logs_after = EmployeeLog.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_employee_password_not_match_negative(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create", {
            "username": "employee_creating",
            "password1": "ihatemyboss",
            "password2": "dontmatch",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "2.0",
        })

        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_passwordsDontMatch' in response.context["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)
    def test_create_employee_email_not_unique_negative(self):
        """ Logged in as an administrator, try to create an employee. email not unique"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create", {
            "username": "employee_creating",
            "password1": "dontmatch",
            "password2": "dontmatch",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "admin1@metronus.es",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "2.0",
        })

        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_emailNotUnique' in response.context["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)

    def test_create_employee_negative_price_negative(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create", {
            "username": "employee_creating",
            "password1": "dontmatch",
            "password2": "dontmatch",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "-1.0",
        })

        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_priceNotValid' in response.context["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)

    def test_create_employee_username_taken_negative(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create", {
            "username": "emp1",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "2.0",
        })

        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_usernameNotUnique' in response.context["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)

    def test_create_employee_invalid_form_negative(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post("/employee/create", {
            "username": "adsfafafaf",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "",
            "last_name": "",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
        })

        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_formNotValid' in response.context["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)
### ----------------Create async----------------------###
    def test_create_employee_positive_async(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post(reverse("employee_create_async"), {
            "username": "employee1",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "1.0"
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

  
    def test_create_employee_password_not_match_negative_async(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post(reverse("employee_create_async"), {
            "username": "employee_creating",
            "password1": "ihatemyboss",
            "password2": "dontmatch",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "2.0",
        })

        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)

        self.assertTrue('employeeCreation_passwordsDontMatch' in data["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)
    def test_create_employee_email_not_unique_negative_async(self):
        """ Logged in as an administrator, try to create an employee. email not unique"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post(reverse("employee_create_async"), {
            "username": "employee_creating",
            "password1": "dontmatch",
            "password2": "dontmatch",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "admin1@metronus.es",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "2.0",
        })

        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)

        self.assertTrue('employeeCreation_emailNotUnique' in data["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)

    def test_create_employee_negative_price_negative_async(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post(reverse("employee_create_async"), {
            "username": "employee_creating",
            "password1": "dontmatch",
            "password2": "dontmatch",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "-1.0",
        })

        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)
        self.assertTrue('employeeCreation_priceNotValid' in data["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)

    def test_create_employee_username_taken_negative_async(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post(reverse("employee_create_async"), {
            "username": "emp1",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "Francisco",
            "last_name": "Romualdo",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
            "price_per_hour": "2.0",
        })

        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)

        self.assertTrue('employeeCreation_usernameNotUnique' in data["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)

    def test_create_employee_invalid_form_negative_async(self):
        """ Logged in as an administrator, try to create an employee"""
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()

        response = c.post(reverse("employee_create_async"), {
            "username": "adsfafafaf",
            "password1": "ihatemyboss",
            "password2": "ihatemyboss",
            "first_name": "",
            "last_name": "",
            "email": "frc@empresa.com",
            "identifier": "frc01",
            "phone": "654321987",
        })

        self.assertEquals(response.status_code, 200)
        # response in bytes must be decode to string
        data = response.content.decode("utf-8")
        # string to dict
        data = json.loads(data)

        self.assertTrue('employeeCreation_formNotValid' in data["errors"])

        # Check that the employee has not been created

        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before, logs_after)
    def test_create_employees_operation_not_allowed(self):
        """
        Invalid operation head
        """
        c = Client()
        c.login(username="admin1", password="123456")        
        response = c.head(reverse("employee_create"))
        self.assertEquals(response.status_code, 403)
    def test_edit_employees_operation_not_allowed(self):
        """
        Invalid operation head
        """
        c = Client()
        c.login(username="admin1", password="123456")        
        response = c.head(reverse("employee_edit",args=("emp1",)))
        self.assertEquals(response.status_code, 403)
###------------List--------------#
    def test_list_employees_positive(self):
        """
        As an admin, list the employees
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["employees"]), 2)
        self.assertTrue(response.context["employees"][0].identifier== "emp01" or response.context["employees"][0].identifier== "emp03")

    def test_list_employees_not_logged(self):
        """
        Try listing the employees without authentication
        """
        c = Client()
        response = c.get("/employee/list")
        self.assertEquals(response.status_code, 403)

    def test_view_employee_positive(self):
        """
        As an admin, view an employee profile
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get(reverse("employee_view",args=("emp1",)))

        self.assertEquals(response.status_code, 200)
        employee = response.context["employee"]
        self.assertTrue(employee)
        self.assertEquals(employee.identifier, "emp01")
        self.assertEquals(employee.user.first_name, "Álvaro")
    def test_view_employee_positive_2(self):
        """
        As a role, view an employee profile with lower role
        """
        c = Client()
        c.login(username="emp3", password="123456")

        response = c.get(reverse("employee_view",args=("emp1",)))

        self.assertEquals(response.status_code, 200)
        employee = response.context["employee"]
        self.assertTrue(employee)
        self.assertEquals(employee.identifier, "emp01")
        self.assertEquals(employee.user.first_name, "Álvaro")

    def test_view_employee_not_allowed(self):
        """
        As an admin, try viewing an employee profile from other company
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/view/emp2/")
        self.assertEquals(response.status_code, 403)

    def test_view_employee_not_allowed_2(self):
            """
            As an employee, try viewing other employee profile
            """
            c = Client()
            c.login(username="emp1", password="123456")

            response = c.get("/employee/view/emp3/")
            self.assertEquals(response.status_code, 403)

    def test_view_employee_404(self):
        """
        Try getting an inexistent employee profile
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/view/marta/")
        self.assertEquals(response.status_code, 404)

    def test_edit_employee_get(self):
        """
        As an admin, get the edit employee form
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/edit/emp1/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["first_name"], "Álvaro")
        self.assertEquals(form.initial["last_name"], "Varo")
        self.assertEquals(form.initial["email"], "emp1@metronus.es")
        self.assertEquals(form.initial["identifier"], "emp01")
        self.assertEquals(form.initial["phone"], "666555444")

    def test_edit_employee_negative_price(self):
        """
        As an admin, edit an employee profile, with negative price
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.post("/employee/edit/emp1/", {
            "first_name": "NuevoNombre",
            "last_name": "NuevoApellido",
            "email": "nuevocorreo@empresa.com",
            "identifier": "nuevoid",
            "phone": "654654654",
            "price_per_hour": "-4.0",
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_priceNotValid' in response.context["errors"])
    def test_edit_employee_negative_invalid_form(self):
        """
        As an admin, edit an employee profile, with blank fields
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="emp1").password
        response = c.post("/employee/edit/emp1/", {
            "first_name": "NuevoNombre",
            "last_name": "NuevoApellido",
            "email": "nuevocorreo@empresa.com",
            "identifier": "",
            "phone": "nuevotelefono",
            "price_per_hour": "",
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue('employeeCreation_formNotValid' in response.context["errors"])


    def test_edit_employee_positive_without_pass(self):
        """
        As an admin, edit an employee profile
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="emp1").password
        logs_before = EmployeeLog.objects.all().count()
        response = c.post("/employee/edit/emp1/", {
            "first_name": "NuevoNombre",
            "last_name": "NuevoApellido",
            "email": "nuevocorreo@empresa.com",
            "identifier": "nuevoid",
            "phone": "654654654",
            "price_per_hour": "4.0",
        })

        self.assertRedirects(response, "/employee/view/emp1/", fetch_redirect_response=False)

        final = Employee.objects.get(user__username="emp1")
        self.assertEquals(final.identifier, "nuevoid")
        self.assertEquals(final.phone, "654654654")
        self.assertEquals(final.user.first_name, "NuevoNombre")
        self.assertEquals(final.user.last_name, "NuevoApellido")
        self.assertEquals(final.user.email, "nuevocorreo@empresa.com")
        self.assertEquals(final.user.password, initialpass)
        self.assertEquals(final.price_per_hour, 4.0)

        # Assert a new log was created with the price change
        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before + 1, logs_after)

    def test_edit_employee_pass_positive(self):
        """
        As an admin, edit an employee password
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="emp1").password

        c.post("/employee/updatePassword/emp1/", {
            "newpass1": "nuevapassword",
            "newpass2": "nuevapassword",
            "currentpass": "123456",
        })

        final = Employee.objects.get(user__username="emp1")
        self.assertTrue(final.user.password != initialpass)

    def test_edit_employee_pass_negative(self):
        """
        As an admin, try editing an employee password when password repeat do not match
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="emp1").password

        c.post("/employee/updatePassword/emp1/", {
            "newpass1": "nuevapassword",
            "newpass2": "ojala morir",
            "currentpass": "123456",
        })

        final = Employee.objects.get(user__username="emp1")
        self.assertTrue(final.user.password == initialpass)

    def test_edit_employee_not_allowed(self):
        """
        Try editing an employee from other company
        """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/employee/edit/emp2/")
        self.assertEquals(response.status_code, 403)

    def test_edit_employee_404(self):
        """
        Try editing an inexistent employee
        """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/employee/edit/diana/")
        self.assertEquals(response.status_code, 404)

    def test_delete_employee_positive(self):
        """
        As an admin, delete an employee from the company and check the log updates
        """
        c = Client()
        c.login(username="admin1", password="123456")

        logs_before = EmployeeLog.objects.all().count()
        self.assertTrue(User.objects.get(username="emp1").is_active)

        response = c.get("/employee/delete/emp1/")
        self.assertRedirects(response, "/employee/list", fetch_redirect_response=False)

        self.assertFalse(User.objects.get(username="emp1").is_active)
        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before + 1, logs_after)

    def test_recover_employee_positive(self):
        """
        As an admin, recover an employee from the company and check the log updates
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/delete/emp1/")
        self.assertRedirects(response, "/employee/list", fetch_redirect_response=False)

        logs_before = EmployeeLog.objects.all().count()
        self.assertFalse(User.objects.get(username="emp1").is_active)

        response = c.get(reverse("employee_recover",args=("emp1",)))
        self.assertRedirects(response, "/employee/list", fetch_redirect_response=False)

        self.assertTrue(User.objects.get(username="emp1").is_active)
        logs_after = EmployeeLog.objects.all().count()
        self.assertEquals(logs_before + 1, logs_after)
