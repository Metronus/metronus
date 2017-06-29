from django.contrib.auth.models import User
from django.test import TestCase, Client
from metronus_app.model.employee import Employee
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.project import Project
from metronus_app.model.company import Company
from metronus_app.model.role import Role
from metronus_app.model.task import Task
from metronus_app.model.administrator import Administrator
from metronus_app.model.department import Department

OK = 200
MOVE = 302
WTF = 400
GTFO = 403
NOTFOUND = 404

class URLAccessTestCase(TestCase):

    def assertResponseCode(self, client, url, expected):
        self.assertEquals(client.get(url).status_code, expected)

    def setUp(self):
        """
        Loads the data to the database for tests to be done
        """
        # Companies
        self.company1 = Company.objects.create(
            cif="A12345678",
            company_name="company1",
            short_name="mplp",
            email="company1@gmail.com",
            phone="123456789"
        )

        self.company2 = Company.objects.create(
            cif="B12312312",
            company_name="company2",
            short_name="lmao",
            email="company2@gmail.com",
            phone="987654321"
        )

        # Admin
        self.admin_user_1 = User.objects.create_user(
            username="admin1",
            password="aaaaaaaa",
            email="admin1@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        self.admin_user_2 = User.objects.create_user(
            username="admin2",
            password="aaaaaaaa",
            email="admin2@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        self.admin1 = Administrator.objects.create(
            user=self.admin_user_1,
            user_type="A",
            identifier="adm01",
            phone="666555444",
            company_id=self.company1
        )

        self.admin2 = Administrator.objects.create(
            user=self.admin_user_2,
            user_type="A",
            identifier="adm02",
            phone="666555444",
            company_id=self.company2
        )

        # Employees
        self.employee0_user = User.objects.create_user(
            username="emp0",
            password="aaaaaaaa",
            email="emp0@metronus.es",
            first_name="Álvaro",
            last_name="Varo"
        )

        self.employee1_user = User.objects.create_user(
            username="emp1",
            password="aaaaaaaa",
            email="emp1@metronus.es",
            first_name="Álvaro",
            last_name="Varo"
        )

        self.employee2_user = User.objects.create_user(
            username="emp2",
            password="aaaaaaaa",
            email="emp2@metronus.es",
            first_name="Alberto",
            last_name="Berto"
        )

        self.employee3_user = User.objects.create_user(
            username="emp3",
            password="aaaaaaaa",
            email="emp3@metronus.es",
            first_name="Alberto",
            last_name="Berto"
        )

        self.employee4_user = User.objects.create_user(
            username="emp4",
            password="aaaaaaaa",
            email="emp4@metronus.es",
            first_name="Alberto",
            last_name="Berto"
        )

        self.employee5_user = User.objects.create_user(
            username="emp5",
            password="aaaaaaaa",
            email="emp5@metronus.es",
            first_name="Alberto",
            last_name="Berto"
        )

        self.employee_inactive_user = User.objects.create_user(
            username="empin",
            password="aaaaaaaa",
            email="empin@metronus.es",
            first_name="Alberto",
            last_name="Berto",
            is_active=False
        )

        self.employee_12_user = User.objects.create_user(
            username="emp12",
            password="aaaaaaaa",
            email="emp12@metronus.es",
            first_name="Alberto",
            last_name="Berto",
        )

        self.employee_21_user = User.objects.create_user(
            username="emp21",
            password="aaaaaaaa",
            email="emp21@metronus.es",
            first_name="Alberto",
            last_name="Berto",
        )

        self.employee_22_user = User.objects.create_user(
            username="emp22",
            password="aaaaaaaa",
            email="emp22@metronus.es",
            first_name="Alberto",
            last_name="Berto",
        )

        self.employee0 = Employee.objects.create(
            user=self.employee0_user,
            user_type="E",
            identifier="emp01",
            phone="666555444",
            company_id=self.company1
        )

        self.employee1 = Employee.objects.create(
            user=self.employee1_user,
            user_type="E",
            identifier="emp01",
            phone="666555444",
            company_id=self.company1
        )

        self.employee2 = Employee.objects.create(
            user=self.employee2_user,
            user_type="E",
            identifier="emp02",
            phone="666555444",
            company_id=self.company1
        )

        self.employee3 = Employee.objects.create(
            user=self.employee3_user,
            user_type="E",
            identifier="emp03",
            phone="666555444",
            company_id=self.company1
        )

        self.employee4 = Employee.objects.create(
            user=self.employee4_user,
            user_type="E",
            identifier="emp04",
            phone="666555444",
            company_id=self.company1
        )

        self.employee5 = Employee.objects.create(
            user=self.employee5_user,
            user_type="E",
            identifier="emp05",
            phone="666555444",
            company_id=self.company1
        )

        self.employee_inactive = Employee.objects.create(
            user=self.employee_inactive_user,
            user_type="E",
            identifier="empin",
            phone="666555444",
            company_id=self.company1
        )

        self.employee12 = Employee.objects.create(
            user=self.employee_12_user,
            user_type="E",
            identifier="empin",
            phone="666555444",
            company_id=self.company1
        )

        self.employee21 = Employee.objects.create(
            user=self.employee_21_user,
            user_type="E",
            identifier="empin",
            phone="666555444",
            company_id=self.company1
        )

        self.employee22 = Employee.objects.create(
            user=self.employee_22_user,
            user_type="E",
            identifier="empin",
            phone="666555444",
            company_id=self.company1
        )

        # Departments
        self.dep1 = Department.objects.create(
            name="Departamento1",
            active=True,
            company_id=self.company1
        )

        self.dep2 = Department.objects.create(
            name="Departamento2",
            active=True,
            company_id=self.company1
        )

        self.dep3 = Department.objects.create(
            name="Departamento3",
            active=True,
            company_id=self.company1
        )

        self.dep_inactive = Department.objects.create(
            name="Departamento4",
            active=False,
            company_id=self.company1
        )

        # Projects
        self.pro1 = Project.objects.create(
            name="Proyecto1",
            deleted=False,
            company_id=self.company1
        )

        self.pro2 = Project.objects.create(
            name="Proyecto2",
            deleted=False,
            company_id=self.company1
        )

        self.pro3 = Project.objects.create(
            name="Proyecto3",
            deleted=False,
            company_id=self.company1
        )

        self.pro_inactive = Project.objects.create(
            name="Proyecto4",
            deleted=True,
            company_id=self.company1
        )

        # Roles
        self.role_ex = Role.objects.create(name="EXECUTIVE", tier=50)
        self.role_pm = Role.objects.create(name="PROJECT_MANAGER", tier=40)
        self.role_co = Role.objects.create(name="COORDINATOR", tier=20)
        self.role_tm = Role.objects.create(name="TEAM_MANAGER", tier=15)
        self.role_em = Role.objects.create(name="EMPLOYEE", tier=10)

        # ProjectDepartments
        self.pd11 = ProjectDepartment.objects.create(project_id=self.pro1, department_id=self.dep1)
        self.pd12 = ProjectDepartment.objects.create(project_id=self.pro1, department_id=self.dep2)
        self.pd13 = ProjectDepartment.objects.create(project_id=self.pro1, department_id=self.dep3)
        self.pd21 = ProjectDepartment.objects.create(project_id=self.pro2, department_id=self.dep1)
        self.pd22 = ProjectDepartment.objects.create(project_id=self.pro2, department_id=self.dep2)
        self.pd23 = ProjectDepartment.objects.create(project_id=self.pro2, department_id=self.dep3)
        self.pd31 = ProjectDepartment.objects.create(project_id=self.pro3, department_id=self.dep1)
        self.pd32 = ProjectDepartment.objects.create(project_id=self.pro3, department_id=self.dep2)
        self.pd33 = ProjectDepartment.objects.create(project_id=self.pro3, department_id=self.dep3)
        self.pd_inactive = ProjectDepartment.objects.create(project_id=self.pro_inactive, department_id=self.dep_inactive)

        # ProjectDepartmentEmployeeRoles
        self.pdrole_1 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd11,
            role_id=self.role_em,
            employee_id=self.employee1
        )

        self.pdrole_2 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd11,
            role_id=self.role_tm,
            employee_id=self.employee2
        )

        self.pdrole_3 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd11,
            role_id=self.role_co,
            employee_id=self.employee3
        )

        self.pdrole_4 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd11,
            role_id=self.role_pm,
            employee_id=self.employee4
        )

        self.pdrole_4_inactive = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd_inactive,
            role_id=self.role_pm,
            employee_id=self.employee4
        )

        self.pdrole_5 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd11,
            role_id=self.role_ex,
            employee_id=self.employee5
        )

        self.pdrole_inactive_user = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd11,
            role_id=self.role_co,
            employee_id=self.employee_inactive
        )

        self.pdrole_12 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd12,
            role_id=self.role_em,
            employee_id=self.employee12
        )

        self.pdrole_21 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd21,
            role_id=self.role_em,
            employee_id=self.employee21
        )

        self.pdrole_22 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=self.pd22,
            role_id=self.role_em,
            employee_id=self.employee22
        )

        self.task1 = Task.objects.create(
            name="Hacer cosas",
            description ="meda",
            actor_id=self.employee5,
            projectDepartment_id=self.pd11,
            production_goal="2.0",
            goal_description="kgs",
            price_per_unit=7.0,
            active=True
        )

        self.task2 = Task.objects.create(
            name="Hacer cosas 2",
            description="meda 2",
            actor_id=self.employee4,
            projectDepartment_id=self.pd22,
            production_goal="4.0",
            goal_description="Peras",
            price_per_unit=8.0,
            active=True
        )

        self.task_inactive = Task.objects.create(
            name="Hacer cosas 3",
            description="meda 3",
            actor_id=self.employee5,
            projectDepartment_id=self.pd11,
            production_goal="2.0",
            goal_description="kgs",
            price_per_unit=7.0,
            active=False
        )

    # Try to access to some URLS as the admin of the company that owns the stuff
    def test_admin_same_company(self):
        c = Client()
        c.login(username="admin1", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", GTFO)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", OK)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", OK)
        self.assertResponseCode(c, "/company/edit/", OK)
        self.assertResponseCode(c, "/administrator/edit/", OK)

        # Projects
        self.assertResponseCode(c, "/project/list", OK)
        self.assertResponseCode(c, "/project/create", OK)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, OK) # Active
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, OK) # Inactive
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, OK)  # Active
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, MOVE)
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, NOTFOUND)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, MOVE)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, NOTFOUND)
        # Non-existent projects
        self.assertResponseCode(c, "/project/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/project/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/project/recover/aaaaa/", NOTFOUND)

        # Departments
        self.assertResponseCode(c, "/department/list", OK)
        self.assertResponseCode(c, "/department/create", OK)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, OK)  # Active
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, OK)  # Active
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, MOVE)
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, NOTFOUND)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, MOVE)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)
        # Non-existent departments
        self.assertResponseCode(c, "/department/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/department/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/department/recover/aaaaa/", NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", OK)
        self.assertResponseCode(c, "/task/create", OK)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, OK)  # Active
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, OK)  # Active
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, MOVE)
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, MOVE)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, NOTFOUND)
        # Non-existent tasks
        self.assertResponseCode(c, "/task/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/task/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/task/recover/aaaaa/", NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", OK)
        self.assertResponseCode(c, "/employee/create", OK)
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee1.user.username, OK)  # Active
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, OK)  # Inactive
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee1.user.username, OK)  # Active
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username, OK)  # Inactive
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee1.user.username, MOVE)
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee1.user.username, NOTFOUND)
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee1.user.username, MOVE)
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee1.user.username, NOTFOUND)
        # Non-existent employees
        self.assertResponseCode(c, "/employee/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/employee/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/employee/recover/aaaaa/", NOTFOUND)

        # Roles
        self.assertResponseCode(c, "/roles/manage", WTF)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, OK)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, OK)
        self.assertResponseCode(c, "/roles/info", OK)
        # Non-existent stuff
        self.assertResponseCode(c, "/roles/manage?employee_id=adfaf", NOTFOUND)
        self.assertResponseCode(c, "/roles/manage?role_id=adada", NOTFOUND)

    # The same stuff as before but from another company
    def test_admin_other_company(self):
        c = Client()
        c.login(username="admin2", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", GTFO)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", OK)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", OK)
        self.assertResponseCode(c, "/company/edit/", OK)
        self.assertResponseCode(c, "/administrator/edit/", OK)

        # Projects
        self.assertResponseCode(c, "/project/list", OK)
        self.assertResponseCode(c, "/project/create", OK)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, GTFO) # Active
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, GTFO) # Inactive
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, GTFO)  # Active
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, GTFO)  # Inactive
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, GTFO)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, NOTFOUND)

        # Departments
        self.assertResponseCode(c, "/department/list", OK)
        self.assertResponseCode(c, "/department/create", OK)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, GTFO)  # Active
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, GTFO)  # Inactive
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, GTFO)  # Active
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, GTFO)  # Inactive
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, GTFO)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", OK)
        self.assertResponseCode(c, "/task/create", OK)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, GTFO)  # Active
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, GTFO)  # Inactive
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, GTFO)  # Active
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, GTFO)  # Inactive
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, GTFO)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", OK)
        self.assertResponseCode(c, "/employee/create", OK)
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee1.user.username, GTFO)  # Active
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, GTFO)  # Inactive
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee1.user.username, GTFO)  # Active
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username, GTFO)  # Inactive
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee1.user.username, GTFO)
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee1.user.username, NOTFOUND)

        # Roles
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, NOTFOUND)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, GTFO)

    # Do stuff as executive
    def test_executive(self):
        c = Client()
        c.login(username="emp5", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", OK)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", OK)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", GTFO)
        self.assertResponseCode(c, "/company/edit/", GTFO)
        self.assertResponseCode(c, "/administrator/edit/", GTFO)

        # Projects
        self.assertResponseCode(c, "/project/list", OK)
        self.assertResponseCode(c, "/project/create", OK)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, OK) # Active
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, OK) # Inactive
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, OK)  # Active
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, MOVE)
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, NOTFOUND)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, MOVE)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, NOTFOUND)
        # Non-existent projects
        self.assertResponseCode(c, "/project/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/project/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/project/recover/aaaaa/", NOTFOUND)

        # Departments
        self.assertResponseCode(c, "/department/list", OK)
        self.assertResponseCode(c, "/department/create", OK)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, OK)  # Active
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, OK)  # Active
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, MOVE)
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, NOTFOUND)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, MOVE)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)
        # Non-existent departments
        self.assertResponseCode(c, "/department/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/department/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/department/recover/aaaaa/", NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", OK)
        self.assertResponseCode(c, "/task/create", OK)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, OK)  # Active
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, OK)  # Active
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, OK)  # Inactive
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, MOVE)
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, MOVE)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, NOTFOUND)
        # Non-existent tasks
        self.assertResponseCode(c, "/task/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/task/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/task/recover/aaaaa/", NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", OK)
        self.assertResponseCode(c, "/employee/create", OK)
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee1.user.username, OK)  # Active
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, OK)  # Inactive
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee1.user.username, OK)  # Active
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username, OK)  # Inactive
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee1.user.username, MOVE)
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee1.user.username, NOTFOUND)
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee1.user.username, MOVE)
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee1.user.username, NOTFOUND)
        # Non-existent employees
        self.assertResponseCode(c, "/employee/view/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/employee/delete/aaaaa/", NOTFOUND)
        self.assertResponseCode(c, "/employee/recover/aaaaa/", NOTFOUND)

        # Roles
        self.assertResponseCode(c, "/roles/manage", WTF)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, OK)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, OK) # Random shitty role
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_5.id, GTFO) # Executive role
        self.assertResponseCode(c, "/roles/info", OK)
        # Non-existent stuff
        self.assertResponseCode(c, "/roles/manage?employee_id=adfaf", NOTFOUND)
        self.assertResponseCode(c, "/roles/manage?role_id=adada", NOTFOUND)

    # Do stuff as project manager
    def test_project_manager(self):
        c = Client()
        c.login(username="emp4", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", OK)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", GTFO)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", GTFO)
        self.assertResponseCode(c, "/company/edit/", GTFO)
        self.assertResponseCode(c, "/administrator/edit/", GTFO)

        # Projects
        self.assertResponseCode(c, "/project/list", OK)
        self.assertResponseCode(c, "/project/create", GTFO)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, OK) # Their project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, GTFO) # Their inactive project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro2.id, GTFO) # Not their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, GTFO)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, GTFO)

        # Departments
        self.assertResponseCode(c, "/department/list", OK)
        self.assertResponseCode(c, "/department/create", GTFO)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, OK)  # Their department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, GTFO)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", OK)
        self.assertResponseCode(c, "/task/create", OK)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, OK)  # Their task
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/view/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, OK)  # Their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, MOVE) # Their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, GTFO)
        # Set it to active again
        self.task1.active = True
        self.task1.save()
        self.assertResponseCode(c, "/task/delete/%d/" % self.task2.id, GTFO) # Not their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task2.id, NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", GTFO)
        self.assertResponseCode(c, "/employee/create", GTFO)

        self.assertResponseCode(c, "/employee/view/emp4/", OK)  # Their own profile
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee12.user.username, OK)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee21.user.username, OK)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/edit/emp4/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee22.user.username,  GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username,  GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/delete/emp4/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/recover/emp4/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        # Roles
        self.assertResponseCode(c, "/roles/manage", GTFO)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, GTFO)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, GTFO) # Random shitty role
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_5.id, GTFO) # Executive role
        self.assertResponseCode(c, "/roles/info", GTFO)

    # Do stuff as coordinator
    def test_coordinator(self):
        c = Client()
        c.login(username="emp3", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", OK)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", GTFO)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", GTFO)
        self.assertResponseCode(c, "/company/edit/", GTFO)
        self.assertResponseCode(c, "/administrator/edit/", GTFO)

        # Projects
        self.assertResponseCode(c, "/project/list", GTFO)
        self.assertResponseCode(c, "/project/create", GTFO)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, GTFO) # Their project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, GTFO) # Their inactive project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro2.id, GTFO) # Not their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, GTFO)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, GTFO)

        # Departments
        self.assertResponseCode(c, "/department/list", OK)
        self.assertResponseCode(c, "/department/create", GTFO)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, OK)  # Their department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, GTFO)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", OK)
        self.assertResponseCode(c, "/task/create", OK)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, OK)  # Their task
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/view/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, OK)  # Their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, MOVE) # Their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, GTFO)
        # Set it to active again
        self.task1.active = True
        self.task1.save()
        self.assertResponseCode(c, "/task/delete/%d/" % self.task2.id, GTFO) # Not their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task2.id, NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", GTFO)
        self.assertResponseCode(c, "/employee/create", GTFO)

        self.assertResponseCode(c, "/employee/view/emp3/", OK)  # Their own profile
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee21.user.username, OK)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/edit/emp3/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee22.user.username,  GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username,  GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/delete/emp3/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/recover/emp3/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        # Roles
        self.assertResponseCode(c, "/roles/manage", GTFO)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, GTFO)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, GTFO) # Random shitty role
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_5.id, GTFO) # Executive role
        self.assertResponseCode(c, "/roles/info", GTFO)

    # Do stuff as team manager (aka the useless role)
    def test_team_manager(self):
        c = Client()
        c.login(username="emp2", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", OK)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", GTFO)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", GTFO)
        self.assertResponseCode(c, "/company/edit/", GTFO)
        self.assertResponseCode(c, "/administrator/edit/", GTFO)

        # Projects
        self.assertResponseCode(c, "/project/list", GTFO)
        self.assertResponseCode(c, "/project/create", GTFO)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, GTFO)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, GTFO)

        # Departments
        self.assertResponseCode(c, "/department/list", GTFO)
        self.assertResponseCode(c, "/department/create", GTFO)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, GTFO)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", GTFO)
        self.assertResponseCode(c, "/task/create", GTFO)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/view/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/delete/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task2.id, NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", GTFO)
        self.assertResponseCode(c, "/employee/create", GTFO)

        self.assertResponseCode(c, "/employee/view/emp2/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/edit/emp2/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/delete/emp2/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/recover/emp2/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        # Roles
        self.assertResponseCode(c, "/roles/manage", GTFO)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, GTFO)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, GTFO)  # Random shitty role
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_5.id, GTFO)  # Executive role
        self.assertResponseCode(c, "/roles/info", GTFO)

    # Do stuff as a normal employee
    def test_employee(self):
        c = Client()
        c.login(username="emp1", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", OK)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", GTFO)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", GTFO)
        self.assertResponseCode(c, "/company/edit/", GTFO)
        self.assertResponseCode(c, "/administrator/edit/", GTFO)

        # Projects
        self.assertResponseCode(c, "/project/list", GTFO)
        self.assertResponseCode(c, "/project/create", GTFO)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, GTFO)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, GTFO)

        # Departments
        self.assertResponseCode(c, "/department/list", GTFO)
        self.assertResponseCode(c, "/department/create", GTFO)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, GTFO)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", GTFO)
        self.assertResponseCode(c, "/task/create", GTFO)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/view/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/delete/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task2.id, NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", GTFO)
        self.assertResponseCode(c, "/employee/create", GTFO)

        self.assertResponseCode(c, "/employee/view/emp1/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/edit/emp1/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/delete/emp1/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/recover/emp1/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        # Roles
        self.assertResponseCode(c, "/roles/manage", GTFO)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, GTFO)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, GTFO)  # Random shitty role
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_5.id, GTFO)  # Executive role
        self.assertResponseCode(c, "/roles/info", GTFO)

    # This employee is very lonely and doesn't have any role
    def test_no_roles(self):
        c = Client()
        c.login(username="emp0", password="aaaaaaaa")

        # Time control
        self.assertResponseCode(c, "/timeLog/list_all/", OK)

        # Dashboard
        self.assertResponseCode(c, "/dashboard/view", GTFO)

        # Company view and edition
        self.assertResponseCode(c, "/company/view/", GTFO)
        self.assertResponseCode(c, "/company/edit/", GTFO)
        self.assertResponseCode(c, "/administrator/edit/", GTFO)

        # Projects
        self.assertResponseCode(c, "/project/list", GTFO)
        self.assertResponseCode(c, "/project/create", GTFO)
        self.assertResponseCode(c, "/project/view/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/view/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro1.id, GTFO)  # Their project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro_inactive.id, GTFO)  # Their inactive project
        self.assertResponseCode(c, "/project/edit/%d/" % self.pro2.id, GTFO)  # Not their project
        self.assertResponseCode(c, "/project/delete/%d/" % self.pro1.id, GTFO)
        self.assertResponseCode(c, "/project/recover/%d/" % self.pro1.id, GTFO)

        # Departments
        self.assertResponseCode(c, "/department/list", GTFO)
        self.assertResponseCode(c, "/department/create", GTFO)
        self.assertResponseCode(c, "/department/view/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/view/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep1.id, GTFO)  # Their department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep_inactive.id, GTFO)  # Their inactive department
        self.assertResponseCode(c, "/department/edit/%d/" % self.dep2.id, GTFO)  # Not their department
        self.assertResponseCode(c, "/department/delete/%d/" % self.dep1.id, GTFO)
        self.assertResponseCode(c, "/department/recover/%d/" % self.dep1.id, NOTFOUND)

        # Tasks
        self.assertResponseCode(c, "/task/list", GTFO)
        self.assertResponseCode(c, "/task/create", GTFO)
        self.assertResponseCode(c, "/task/view/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/view/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/view/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task_inactive.id, GTFO)  # Their inactive task
        self.assertResponseCode(c, "/task/edit/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/delete/%d/" % self.task1.id, GTFO)  # Their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task1.id, NOTFOUND)
        self.assertResponseCode(c, "/task/delete/%d/" % self.task2.id, GTFO)  # Not their task
        self.assertResponseCode(c, "/task/recover/%d/" % self.task2.id, NOTFOUND)

        # Employees
        self.assertResponseCode(c, "/employee/list", GTFO)
        self.assertResponseCode(c, "/employee/create", GTFO)

        self.assertResponseCode(c, "/employee/view/emp0/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/view/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/edit/emp0/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/edit/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/delete/emp0/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/delete/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        self.assertResponseCode(c, "/employee/recover/emp0/", GTFO)  # Their own profile
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee12.user.username, GTFO)  # User in their project but not their department
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee21.user.username, GTFO)  # User in their department but not their project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee22.user.username, GTFO)  # User not in their department or project
        self.assertResponseCode(c, "/employee/recover/%s/" % self.employee_inactive.user.username, GTFO)  # User in their dep and proj but inactive

        # Roles
        self.assertResponseCode(c, "/roles/manage", GTFO)
        self.assertResponseCode(c, "/roles/manage?employee_id=%d" % self.employee1.id, GTFO)
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_1.id, GTFO)  # Random shitty role
        self.assertResponseCode(c, "/roles/manage?role_id=%d" % self.pdrole_5.id, GTFO)  # Executive role
        self.assertResponseCode(c, "/roles/info", GTFO)



