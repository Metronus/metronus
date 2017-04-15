from django.contrib.auth.models                       import User
from django.test                                      import TestCase, Client
from django.core.exceptions                           import ObjectDoesNotExist, PermissionDenied

from metronus_app.model.employee                      import Employee
from metronus_app.model.projectDepartment             import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.task                          import Task
from metronus_app.model.timeLog                       import TimeLog
from metronus_app.model.project                       import Project
from metronus_app.model.company                       import Company
from metronus_app.model.role                          import Role
from metronus_app.model.administrator                 import Administrator
from metronus_app.model.department                    import Department

import string, random, json

def ranstr():
    """Returns a 10-character random string"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

### Son herramientas sorpresa que nos ayudarán más tarde

def checkJsonMetricsAreEqual(self, response_string, data):
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

def createEmployeeInProjDept(project, department):
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

    return employee

def createTaskInProjDept(project, department):
    """
    creates a task for a given project and department
    """
    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

    Task.objects.create(
        name = ranstr(),
        description = ranstr(),
        actor_id = Administrator.objects.get(identifier="adm01"),
        projectDepartment_id = pd
    )

def createTimelogInTask(task, duration, date, employee = None):
    """
    creates a timelog for an employee involving a task during a specific date
    """
    TimeLog.objects.create(
        description = ranstr(),
        workDate = date,
        duration = duration,
        task_id = task,
        employee_id = Employee.objects.get(identifier="emp01") if employee is None else employee
    )

################################## Party hard a partir de aquí ##################################

class DepartmentMetricsTestCase(TestCase):
    """This class provides a test case for accessing department-related metrics"""
    def setUp(self):

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
            company_id=company1
        )

        dep1 = Department.objects.create(
            name="Departamento1",
            active=True,
            company_id=company1
        )

        dep2 = Department.objects.create(
            name="Departamento2",
            active=True,
            company_id=company1
        )

        dep3 = Department.objects.create(
            name="Departamento3",
            active=True,
            company_id=company1
        )

        dep4 = Department.objects.create(
            name="Departamento4",
            active=True,
            company_id=company1
        )

        dep5 = Department.objects.create(
            name="Departamento5",
            active=True,
            company_id=company2
        )

        dep_rand = Department.objects.create(
            name="Dep_rand",
            active=True,
            company_id=company1
        )

        role_ex = Role.objects.create(name="EXECUTIVE", tier=50)
        role_pm = Role.objects.create(name="PROJECT_MANAGER", tier=40)
        role_tm = Role.objects.create(name="TEAM_MANAGER", tier=30)
        role_co = Role.objects.create(name="COORDINATOR", tier=20)
        role_em = Role.objects.create(name="EMPLOYEE", tier=10)

        pro1 = Project.objects.create(name="pro1", deleted=False, company_id=company1)
        pro2 = Project.objects.create(name="pro2", deleted=False, company_id=company2)
        pro3 = Project.objects.create(name="pro3", deleted=False, company_id=company1)
        pro4 = Project.objects.create(name="pro4", deleted=False, company_id=company1)
        pro_random = Project.objects.create(name="pro_random", deleted=False, company_id=company1)

        pd = ProjectDepartment.objects.create(project_id=pro1, department_id=dep2)
        pd2 = ProjectDepartment.objects.create(project_id=pro1, department_id=dep_rand)

        pdrole1 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id = pd,
            role_id = role_tm,
            employee_id = employee1
        )

        pdrole2 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id = pd,
            role_id = role_ex,
            employee_id = employee2
        )

        pdrole3 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id = pd2,
            role_id = role_ex,
            employee_id = employee2
        )

    def test_access_denied_not_logged_emppertask(self):
        """
        Without authentication, try getting the emppertask JSON
        """
        c = Client()

        response = c.get("/department/ajaxEmployeesPerTask?department_id=%d" % Department.objects.get(name="Departamento2").id)
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_emppertask(self):
        """
        Without proper roles, try getting the emppertask JSON
        """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/department/ajaxEmployeesPerTask?department_id=%d" % Department.objects.get(name="Departamento2").id)
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_emppertask(self):
        """
        As an executive, try getting the emppertask JSON
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/department/ajaxEmployeesPerTask?department_id=%d" % Department.objects.get(name="Departamento2").id)
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_emppertask(self):
        """
        As an executive, try getting the emppertask JSON from other company
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/department/ajaxEmployeesPerTask?department_id=%d" % Department.objects.get(name="Departamento5").id)
        self.assertEquals(response.status_code, 403)

    def test_bad_request_emppertask(self):
        """
        Try getting the emppertask JSON without providing a department
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/department/ajaxEmployeesPerTask")
        self.assertEquals(response.status_code, 400)
    
    def test_random_data_emppertask(self):
        """
        Does a lot of random test and checks the data generate matches the emppertask JSON
        """
        c = Client()
        c.login(username="admin1", password="123456")

        department = Department.objects.get(name="Dep_rand")
        projects = Project.objects.filter(company_id__company_name="company1")

        # Make the test run 1 time (this one's slow af)
        for _ in range(1):

            TimeLog.objects.all().delete()
            Task.objects.all().delete()

            true_data = {'names': [], 'values': []}

            for project in projects:

                # Create between 1 and 5 tasks for the current project and the department
                for _ in range(random.randint(1,5)):
                    createTaskInProjDept(project, department)

                for task in Task.objects.filter(projectDepartment_id__department_id = department, projectDepartment_id__project_id = project):
                    # Create between 2 and 20 employees, that will assign time to that task
                    num_employees = random.randint(2,20)
                    true_data['names'].append(task.name)
                    true_data['values'].append(num_employees)

                    for _ in range(num_employees):
                        employee = createEmployeeInProjDept(project, department)

                        # Make them create time logs
                        for _ in range(random.randint(1,3)):
                            createTimelogInTask(task, 100, "2016-01-01 10:00+00:00", employee)

        response = c.get("/department/ajaxEmployeesPerTask?department_id=%d" % Department.objects.get(name="Dep_rand").id)
        self.assertEquals(response.status_code, 200)
        checkJsonMetricsAreEqual(self, str(response.content, encoding='utf8'), true_data)
    
    def test_access_denied_not_logged_timepertask(self):
        """
        Try getting the timepertask JSON without authentication
        """
        c = Client()

        response = c.get("/department/ajaxTimePerTask?department_id=%d" % Department.objects.get(name="Departamento2").id)
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_timepertask(self):
        """
        Try getting the timepertask JSON without proper roles
        """
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/department/ajaxTimePerTask?department_id=%d" % Department.objects.get(name="Departamento2").id)
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_timepertask(self):
        """
        Try getting the timepertask JSON as an executive
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/department/ajaxTimePerTask?department_id=%d" % Department.objects.get(name="Departamento2").id)
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_timepertask(self):
        """
        Try getting the timepertask JSON without as an executive from other company
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/department/ajaxTimePerTask?department_id=%d" % Department.objects.get(name="Departamento5").id)
        self.assertEquals(response.status_code, 403)

    def test_bad_request_timepertask(self):
        """
        Try getting the timepertask JSON without providing a department
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/department/ajaxTimePerTask")
        self.assertEquals(response.status_code, 400)

    def test_random_data_timepertask(self):
        """
        Does a lot of test and checks the data matches the timepertask JSON
        """
        c = Client()
        c.login(username="admin1", password="123456")

        department = Department.objects.get(name="Dep_rand")
        projects = Project.objects.filter(company_id__company_name="company1")

        # Make the test run 5 times
        for _ in range(5):

            TimeLog.objects.all().delete()
            Task.objects.all().delete()

            true_data = {'names': [], 'values': []}

            for project in projects:

                # Create between 1 and 5 tasks for the current project and the department
                for _ in range(random.randint(1,5)):
                    createTaskInProjDept(project, department)

                for task in Task.objects.filter(projectDepartment_id__department_id = department, projectDepartment_id__project_id = project):
                    # Create between 2 and 10 employees, that will assign time to that task
                    num_employees = random.randint(2,10)
                    used_time = 0

                    for _ in range(num_employees):
                        employee = createEmployeeInProjDept(project, department)

                        # Make them create time logs (between 1 and 3)
                        for _ in range(random.randint(1,3)):
                            count = random.choice([True, True, True, False]) # 25% chance of being outside of the requested time margin
                            date_worked = "2016-06-01 10:00+01:00" if count else "2014-01-01 10:00+00:00"
                            time_worked = random.randint(1, 1000)

                            createTimelogInTask(task, time_worked, date_worked, employee)

                            if count:
                                used_time += time_worked

                    true_data['names'].append(task.name)
                    true_data['values'].append(used_time)

        response = c.get("/department/ajaxTimePerTask?department_id=%d&start_date=2016-01-01&end_date=2016-12-31" % Department.objects.get(name="Dep_rand").id)
        self.assertEquals(response.status_code, 200)
        checkJsonMetricsAreEqual(self, str(response.content, encoding='utf8'), true_data)