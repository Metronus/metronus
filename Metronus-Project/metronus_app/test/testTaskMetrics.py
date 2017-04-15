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
    """ Returns a 10-character random string"""
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
    creates a task for a given project and department, either with production goal or not
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


class TaskMetricsTestCase(TestCase):
    """This class provides a test case for accessing task-related metrics"""
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
            projectDepartment_id=pd,
            role_id=role_tm,
            employee_id=employee1
        )

        pdrole2 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd,
            role_id=role_ex,
            employee_id=employee2
        )

        pdrole3 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd2,
            role_id=role_ex,
            employee_id=employee2
        )
        task1 = Task.objects.create(
            name  ="Hacer cosas",
            description  = "meda",
            actor_id = employee1,
            projectDepartment_id = pd
        )

        task2 = Task.objects.create(
            name  ="Hacer cosas de back",
            description  = "hola",
            actor_id = employee1,
            projectDepartment_id = pd
        )

        task3 = Task.objects.create(
            name  ="Hacer cosas de front",
            description  = "nada",
            actor_id = employee2,
            projectDepartment_id = pd2,
            production_goal="2.0",
            goal_description="kgs"
        )

     
    def test_access_denied_not_logged_prod_task(self):
        """
        Without authentication, try getting the prod_per_task JSON
        """
        c = Client()

        response = c.get("/task/ajaxProdPerTask?task_id=%d" % Task.objects.all().first().id)
        
        #redirected to login
        self.assertEquals(response.status_code, 302)
        
    def test_access_ok_logged_prod_task(self):
        """
        With proper roles, get the prod_per_task JSON
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/task/ajaxProdPerTask?task_id=%d" % Task.objects.all().first().id)
        self.assertEquals(response.status_code, 200)

    def test_bad_request_prod_per_task(self):
        """
        Get the prod_per_task JSON without providing a task id
        """
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/task/ajaxProdPerTask")
        self.assertEquals(response.status_code, 400)