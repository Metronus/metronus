from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist
from metronus_app.model.employee import Employee
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.task import Task
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.model.role import Role
from metronus_app.model.administrator import Administrator
from metronus_app.model.department import Department
from metronus_app.common_utils import check_json_metrics_are_equal, ranstr
import random


class EmployeeMetricsTestCase(TestCase):
    """This class provides a test case for accessing employee-related metrics"""
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
        admin_user2 = User.objects.create_user(
            username="admin2",
            password="123456",
            email="admin2@metronus.es",
            first_name="Pepito2",
            last_name="Pérez2"
        )

        # Admin 2
        Administrator.objects.create(
            user=admin_user2,
            user_type="A",
            identifier="adm02",
            phone="666555444",
            company_id=company2
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
            company_id=company1
        )

        # dep1
        Department.objects.create(
            name="Departamento1",
            active=True,
            company_id=company1
        )

        dep2 = Department.objects.create(
            name="Departamento2",
            active=True,
            company_id=company1
        )

        Department.objects.create(
            name="Departamento3",
            active=True,
            company_id=company1
        )

        # dep4
        Department.objects.create(
            name="Departamento4",
            active=True,
            company_id=company1
        )

        # dep5
        Department.objects.create(
            name="Departamento5",
            active=True,
            company_id=company1
        )

        role_ex = Role.objects.create(name="EXECUTIVE", tier=50)
        # role_pm
        Role.objects.create(name="PROJECT_MANAGER", tier=40)
        role_tm = Role.objects.create(name="TEAM_MANAGER", tier=30)
        # roleco
        Role.objects.create(name="COORDINATOR", tier=20)
        # role_em
        Role.objects.create(name="EMPLOYEE", tier=10)

        pro1 = Project.objects.create(name="pro1", deleted=False, company_id=company1)
        # pro2
        Project.objects.create(name="pro2", deleted=False, company_id=company2)
        # pro3
        Project.objects.create(name="pro_random", deleted=False, company_id=company1)

        pd = ProjectDepartment.objects.create(project_id=pro1, department_id=dep2)

        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd,
            role_id=role_tm,
            employee_id=employee1
        )

        # pdrole2
        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd,
            role_id=role_ex,
            employee_id=employee2
        )
    def test_access_denied_not_logged_prod_task(self):
        """
        Without authentication, try getting the prod_per_task JSON
        """
        c = Client()

        response = c.get("/employee/ajax_productivity_per_task/{0}".format(Employee.objects.all().first().user.username))

        # redirected to login
        self.assertEquals(response.status_code, 302)

    def test_access_ok_logged_prod_task(self):
        """
        With proper roles, get the prod_per_task JSON
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/ajax_productivity_per_task/{0}".format( Employee.objects.get(identifier="emp01").user.username))
        self.assertEquals(response.status_code, 200)

    def test_bad_request_prod_task(self):
        """
        Get the productivity JSON without providing a employee id
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/employee/ajax_productivity_per_task/")
        self.assertEquals(response.status_code, 404)

    def test_access_denied_not_logged_profit(self):
        """
        Without authentication, try getting the profit JSON
        """
        c = Client()

        response = c.get("/employee/ajaxProfit/{0}/" .format( Employee.objects.get(identifier="emp01").id))
        self.assertEquals(response.status_code, 302)


    def test_access_ok_executive_profit(self):
        """
        As an executive, try getting the profit JSON
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/employee/ajaxProfit/{0}/" .format(Employee.objects.get(identifier="emp01").id))
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_profit(self):
        """
        As an executive, try getting the profit JSON from other company
        """
        c = Client()
        c.login(username="admin2", password="123456")

        response = c.get("/employee/ajaxProfit/{0}/" .format(Employee.objects.get(identifier="emp01").id))
        self.assertEquals(response.status_code, 403)

    def test_bad_request_profit(self):
        """
        Try getting the profit JSON without providing a department
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/employee/ajaxProfit/")
        self.assertEquals(response.status_code, 404)

    def test_prod_per_task_date_bad_start_date(self):
        """
        Request the prod_per_task_and_date with a wrong start date
        """

        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/ajax_productivity_per_task_and_date/{0}?start_date=20101-01&end_date=2017-01-01"
            .format(Employee.objects.get(identifier="emp01").user.username))
        self.assertEquals(response.status_code, 400)
           
    def test_prod_per_task_date_bad_end_date(self):
        """
        Request the prod_per_task_date with a wrong end date
        """

        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/ajax_productivity_per_task_and_date/{0}?start_date=2016-01-01&end_date=20101-01"
            .format(Employee.objects.get(identifier="emp01").user.username))
        self.assertEquals(response.status_code, 400)
           
    def test_prod_per_task_date_bad_end_offset(self):
        """
        Request the prod_per_task_date with a wrong offset
        """

        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/employee/ajax_productivity_per_task_and_date/{0}?offset=+53:20"
            .format(Employee.objects.get(identifier="emp01").user.username))
        self.assertEquals(response.status_code, 400)
