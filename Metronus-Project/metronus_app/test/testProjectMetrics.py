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

import string
import random
import json


def check_json_metrics_are_equal(self, response_string, data):
    """
    Checks the data provided by the JSON equals the real data
    """
    response = json.loads(response_string)

    self.assertTrue('names' in response)
    self.assertTrue('values' in response)

    self.assertEquals(len(response['names']), len(data['names']))
    self.assertEquals(len(response['values']), len(data['values']))

    for (name, val) in zip(data['names'], data['values']):
        self.assertTrue(name in response['names'])
        self.assertTrue(val in response['values'])

        ind = response['names'].index(name)

        self.assertEquals(val, response['values'][ind])


def ranstr():
    """Returns a 10-character random string"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


class ProjectMetricsTestCase(TestCase):
    """This class provides a test case for accessing project-related metrics"""
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

    def test_access_denied_not_logged_empperdmtp(self):
        """
        Without authentication, try getting the empperdmtp JSON
        """
        c = Client()

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id={0}".format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_empperdmtp(self):
        """
        Without proper roles, try getting the empperdmtp JSON
        """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_empperdmtp(self):
        """
        As an executive, try getting the empperdmtp JSON
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_empperdmtp(self):
        """
        As an executive, try getting the empperdmtp JSON from other company
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id={0}" .format(Project.objects.get(name="pro2").id))
        self.assertEquals(response.status_code, 403)

    def test_bad_request_empperdmtp(self):
        """
        Try getting the empperdmtp JSON without providing a project
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt")
        self.assertEquals(response.status_code, 400)

    def test_random_data_empperdmtp(self):
        """
        Does a lot of random test and checks the data generate matches the empperdmtp JSON
        """
        def create_employee_in_projdept(project, department):
            """
            creates an employee and assigns him/her a new role
            """
            user = User.objects.create_user(
                username=ranstr(),
                password=ranstr(),
                email=ranstr() + "@metronus.es",
                first_name=ranstr(),
                last_name=ranstr()
            )

            employee = Employee.objects.create(
                user=user,
                user_type="E",
                identifier=ranstr(),
                phone="123123123",
                company_id=Company.objects.get(company_name="company1")
            )

            try:
                pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
            except ObjectDoesNotExist:
                pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

            role = Role.objects.get(tier=random.choice([10, 20, 30, 40, 50]))
            ProjectDepartmentEmployeeRole.objects.create(projectDepartment_id=pd, role_id=role, employee_id=employee)

        c = Client()
        c.login(username="admin1", password="123456")

        departments = Department.objects.filter(company_id__company_name="company1")
        project = Project.objects.get(name="pro_random")

        n_dep = len(departments)

        # Do the random test 5 times
        for k in range(5):
            ProjectDepartmentEmployeeRole.objects.all().delete()

            employees_per_dpmt = [random.choice(range(11)) for _ in range(n_dep)]
            true_data = {'names': [], 'values': []}

            for i in range(n_dep):
                dpmt = departments[i]
                employee_count = employees_per_dpmt[i]

                true_data['names'].append(dpmt.name)
                true_data['values'].append(employee_count)

                for _ in range(employee_count):
                    create_employee_in_projdept(project, dpmt)

            # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/project/ajaxEmployeesPerDpmt?project_id={0}" .format(project.id))
            self.assertEquals(response.status_code, 200)
            check_json_metrics_are_equal(self, str(response.content, encoding='utf8'), true_data)

    def test_access_denied_not_logged_tasksperdmtp(self):
        """
        Without authentication, try getting the tasksperdmtp JSON
        """
        c = Client()

        response = c.get("/project/ajaxTasksPerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_tasksperdmtp(self):
        """
        Without proper roles, try getting the tasksperdmtp JSON
        """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_tasksperdmtp(self):
        """
        Try getting the tasksperdmtp JSON as an executive
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_tasksperdmtp(self):
        """
        Try getting the tasksperdmtp JSON without as an executive from other company
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt?project_id={0}" .format(Project.objects.get(name="pro2").id))
        self.assertEquals(response.status_code, 403)

    def test_bad_request_tasksperdmtp(self):
        """
        Try getting the tasksperdmtp JSON without providing a project
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt")
        self.assertEquals(response.status_code, 400)

    def test_random_data_tasksperdmtp(self):
        """
        Does a lot of random test and checks the data generate matches the tasksperdmtp JSON
        """
        def create_task_in_projdept(project, department):
            """
            creates a task for a given project and department
            """
            try:
                pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
            except ObjectDoesNotExist:
                pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

            Task.objects.create(
                name=ranstr(),
                description=ranstr(),
                actor_id=Administrator.objects.get(identifier="adm01"),
                projectDepartment_id=pd
            )

        c = Client()
        c.login(username="admin1", password="123456")

        departments = Department.objects.filter(company_id__company_name="company1")
        project = Project.objects.get(name="pro_random")

        n_dep = len(departments)
        # Do the random test 5 times
        for k in range(5):
            Task.objects.all().delete()

            tasks_per_dpmt = [random.choice(range(11)) for _ in range(n_dep)]
            true_data = {'names': [], 'values': []}

            for i in range(n_dep):
                dpmt = departments[i]
                task_count = tasks_per_dpmt[i]

                true_data['names'].append(dpmt.name)
                true_data['values'].append(task_count)

                for _ in range(task_count):
                    create_task_in_projdept(project, dpmt)

            # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/project/ajaxTasksPerDpmt?project_id={0}" .format(project.id))
            self.assertEquals(response.status_code, 200)
            check_json_metrics_are_equal(self, str(response.content, encoding='utf8'), true_data)

    def test_access_denied_not_logged_timeperdpmt(self):
        """
        Try getting the timeperdpmt JSON without authentication
        """
        c = Client()

        response = c.get("/project/ajaxTimePerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_timeperdpmt(self):
        """
        Try getting the timeperdpmt JSON without proper roles
        """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/project/ajaxTimePerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_timeperdpmt(self):
        """
        Try getting the timeperdpmt JSON as an executive
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTimePerDpmt?project_id={0}" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_timeperdpmt(self):
        """
        Try getting the timeperdpmt JSON without as an executive from other company
        """

        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTimePerDpmt?project_id={0}" .format(Project.objects.get(name="pro2").id))
        self.assertEquals(response.status_code, 403)

    def test_bad_request_timeperdpmt(self):
        """
        Try getting the timeperdpmt JSON without providing a project
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTimePerDpmt")
        self.assertEquals(response.status_code, 400)

    def test_random_data_timeperdpmt(self):
        """
        Does a lot of test and checks the data matches the timeperdpmt JSON
        """
        def create_timelog_in_task(task, duration, date):
            """
            creates a timelog for an employee involving a task during a specific date
            """
            TimeLog.objects.create(
                description=ranstr(),
                workDate=date,
                duration=duration,
                task_id=task,
                employee_id=Employee.objects.get(identifier="emp01")
            )

        def create_task_in_projdept(project, department):
            """
            creates a task for a given project and department
            """
            try:
                pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
            except ObjectDoesNotExist:
                pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

            Task.objects.create(
                name=ranstr(),
                description=ranstr(),
                actor_id=Administrator.objects.get(identifier="adm01"),
                projectDepartment_id=pd
            )

        c = Client()
        c.login(username="admin1", password="123456")

        departments = Department.objects.filter(company_id__company_name="company1")
        project = Project.objects.get(name="pro_random")

        n_dep = len(departments)
        # Do the random test 5 times

        for k in range(5):

            # Remove all tasks and time logs
            TimeLog.objects.all().delete()
            Task.objects.all().delete()

            true_data = {'names': [], 'values': []}

            for i in range(n_dep):
                dpmt = departments[i]

                # Create between 1 and 4 tasks for each department
                for _ in range(random.randint(1, 4)):
                    create_task_in_projdept(project, dpmt)

                # Initialize the true data for this department
                used_time = 0

                # Create between 1 and 20 timelogs for each department
                for _ in range(random.randint(1, 20)):
                    duration = random.randint(1, 100)
                    task = random.choice(Task.objects.filter(projectDepartment_id__project_id=project,
                                                             projectDepartment_id__department_id=dpmt))
                    measure = random.choice([True, True, True, False])  # Make timelogs have a 25% chance of not being counted towards the metric
                    date = "2016-06-01 10:00+00:00" if measure else "2014-05-01 21:00+00:00"

                    create_timelog_in_task(task, duration, date)

                    if measure:
                        used_time += duration

                true_data['names'].append(dpmt.name)
                true_data['values'].append(used_time)

            # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/project/ajaxTimePerDpmt?project_id={0}&start_date=2016-01-01&end_date=2017-01-01" .format(project.id))
            self.assertEquals(response.status_code, 200)
            check_json_metrics_are_equal(self, str(response.content, encoding='utf8'), true_data)

    def test_access_denied_not_logged_profit(self):
        """
        Without authentication, try getting the profit JSON
        """
        c = Client()

        response = c.get("/project/ajaxProfit/{0}/" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_profit(self):
        """
        Without proper roles, try getting the profit JSON
        """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/project/ajaxProfit/{0}/" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_profit(self):
        """
        As an executive, try getting the profit JSON
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxProfit/{0}/" .format(Project.objects.get(name="pro1").id))
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_profit(self):
        """
        As an executive, try getting the profit JSON from other company
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxProfit/{0}/" .format(Project.objects.get(name="pro2").id))
        self.assertEquals(response.status_code, 403)

    def test_bad_request_profit(self):
        """
        Try getting the profit JSON without providing a department
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxProfit")
        self.assertEquals(response.status_code, 404)
