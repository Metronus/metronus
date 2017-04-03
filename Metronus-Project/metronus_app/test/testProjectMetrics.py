from metronus_app.model.project                       import Project
from metronus_app.model.company                       import Company
from metronus_app.controllers.projectController       import *
from metronus_app.model.role                          import Role
from django.contrib.auth.models                       import User
from django.test                                      import TestCase, Client
from metronus_app.model.employee                      import Employee
from django.core.exceptions                           import ObjectDoesNotExist, PermissionDenied
from metronus_app.model.projectDepartment             import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.core.exceptions                           import ObjectDoesNotExist
from metronus_app.model.task                          import Task
        
import string, random

def ranstr():
    # Returns a 10-character random string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

class ProjectMetricsTestCase(TestCase):

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
            company_id=company1
        )

        role_ex = Role.objects.create(name="EXECUTIVE", tier=50)
        role_pm = Role.objects.create(name="PROJECT_MANAGER", tier=40)
        role_tm = Role.objects.create(name="TEAM_MANAGER", tier=30)
        role_co = Role.objects.create(name="COORDINATOR", tier=20)
        role_em = Role.objects.create(name="EMPLOYEE", tier=10)

        pro1 = Project.objects.create(name="pro1", deleted=False, company_id=company1)
        pro2 = Project.objects.create(name="pro2", deleted=False, company_id=company2)
        pro_random = Project.objects.create(name="pro_random", deleted=False, company_id=company1)

        pd = ProjectDepartment.objects.create(project_id=pro1, department_id=dep2)

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

    def test_access_denied_not_logged_empperdmtp(self):
        c = Client()

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id=%d" % Project.objects.get(name="pro1").id)
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_empperdmtp(self):
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id=%d" % Project.objects.get(name="pro1").id)
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_empperdmtp(self):
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id=%d" % Project.objects.get(name="pro1").id)
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_empperdmtp(self):
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt?project_id=%d" % Project.objects.get(name="pro2").id)
        self.assertEquals(response.status_code, 403)

    def test_bad_request_empperdmtp(self):
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxEmployeesPerDpmt")
        self.assertEquals(response.status_code, 400)
    
    def test_random_data_empperdmtp(self):

        def createEmployeeInProjDept(project, department):
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


        # Do the random test 10 times
        for k in range(10):
            ProjectDepartmentEmployeeRole.objects.all().delete()
            employees_per_dpmt = [random.choice(range(11)) for _ in range(len(departments))]
            true_data = {}

            for i in range(len(departments)):
                dpmt = departments[i]
                employee_count = employees_per_dpmt[i]

                true_data[str(dpmt.id)] = {
                                        'name': dpmt.name,
                                        'employees': employee_count
                                     }

                for _ in range(employee_count):
                    createEmployeeInProjDept(project, dpmt)

            # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/project/ajaxEmployeesPerDpmt?project_id=%d" % project.id)
            self.assertEquals(response.status_code, 200)
            self.assertJSONEqual(str(response.content, encoding='utf8'), true_data)

    def test_access_denied_not_logged_tasksperdmtp(self):
        c = Client()

        response = c.get("/project/ajaxTasksPerDpmt?project_id=%d" % Project.objects.get(name="pro1").id)
        self.assertEquals(response.status_code, 403)

    def test_access_denied_low_role_tasksperdmtp(self):
        c = Client()
        c.login(username="emp1", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt?project_id=%d" % Project.objects.get(name="pro1").id)
        self.assertEquals(response.status_code, 403)

    def test_access_ok_executive_tasksperdmtp(self):
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt?project_id=%d" % Project.objects.get(name="pro1").id)
        self.assertEquals(response.status_code, 200)

    def test_access_other_company_executive_tasksperdmtp(self):
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt?project_id=%d" % Project.objects.get(name="pro2").id)
        self.assertEquals(response.status_code, 403)

    def test_bad_request_tasksperdmtp(self):
        c = Client()
        c.login(username="emp2", password="123456")

        response = c.get("/project/ajaxTasksPerDpmt")
        self.assertEquals(response.status_code, 400)

    def test_random_data_tasksperdmtp(self):

        def createTaskInProjDept(project, department):

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

        c = Client()
        c.login(username="admin1", password="123456")

        departments = Department.objects.filter(company_id__company_name="company1")
        project = Project.objects.get(name="pro_random")

        # Do the random test 10 times
        for k in range(10):
            Task.objects.all().delete()
            tasks_per_dpmt = [random.choice(range(11)) for _ in range(len(departments))]
            true_data = {}

            for i in range(len(departments)):
                dpmt = departments[i]
                task_count = tasks_per_dpmt[i]

                true_data[str(dpmt.id)] = {
                                        'name': dpmt.name,
                                        'tasks': task_count
                                     }

                for _ in range(task_count):
                    createTaskInProjDept(project, dpmt)

            # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/project/ajaxTasksPerDpmt?project_id=%d" % project.id)
            self.assertEquals(response.status_code, 200)
            self.assertJSONEqual(str(response.content, encoding='utf8'), true_data)