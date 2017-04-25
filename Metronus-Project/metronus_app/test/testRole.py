from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist

from metronus_app.model.employee import Employee
from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.projectDepartment import ProjectDepartment


class RoleTestCase(TestCase):
    """This class provides a test case for using and managing roles"""
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

        employee3_user = User.objects.create_user(
            username="emp3",
            password="123456",
            email="emp3@metronus.es",
            first_name="Mequiero",
            last_name="Morir"
        )

        employee1 = Employee.objects.create(
            user=employee1_user,
            user_type="E",
            identifier="emp01",
            phone="666555444",
            company_id=company1
        )

        # Employee 2
        Employee.objects.create(
            user=employee2_user,
            user_type="E",
            identifier="emp02",
            phone="666555444",
            company_id=company1
        )

        employee3 = Employee.objects.create(
            user=employee3_user,
            user_type="E",
            identifier="emp03",
            phone="666555444",
            company_id=company1
        )

        project1 = Project.objects.create(
            company_id=company1,
            name="proyecto 1",
        )

        project2 = Project.objects.create(
            company_id=company1,
            name="proyecto 2",
        )

        # Project 3
        Project.objects.create(
            company_id=company2,
            name="proyecto 3",
        )

        department1 = Department.objects.create(
            company_id=company1,
            name="departamento 1",
        )

        department2 = Department.objects.create(
            company_id=company1,
            name="departamento 2",
        )

        # Department 3
        Department.objects.create(
            company_id=company2,
            name="departamento 3",
        )

        projdept1 = ProjectDepartment.objects.create(
            project_id=project1,
            department_id=department1
        )

        # ProjDept2
        ProjectDepartment.objects.create(
            project_id=project1,
            department_id=department2
        )

        # ProjDept3
        ProjectDepartment.objects.create(
            project_id=project2,
            department_id=department1
        )

        # role_pm
        Role.objects.create(name="PROJECT_MANAGER", tier=40)

        role_tm = Role.objects.create(name="TEAM_MANAGER", tier=30)
        role_co = Role.objects.create(name="COORDINATOR", tier=20)

        # role_em
        Role.objects.create(name="EMPLOYEE", tier=10)

        # EmpRole1
        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=projdept1,
            employee_id=employee1,
            role_id=role_tm,
        )

        # EmpRole2
        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=projdept1,
            employee_id=employee3,
            role_id=role_co,
        )

    def test_get_form_not_logged(self):
        """
        Try managing the roles without authentication
        """
        c = Client()
        response = c.get("/roles/manage")
        self.assertEquals(response.status_code, 403)

    def test_get_form_admin_without_params(self):
        """
        Try managing the roles providing proper parameters
        """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/roles/manage")
        self.assertEquals(response.status_code, 400)

    def test_get_form_admin_ok(self):
        """
        As an admin, get the role edit form for an employee
        """
        c = Client()
        c.login(username="admin1", password="123456")
        emp = Employee.objects.get(identifier="emp01")
        response = c.get("/roles/manage?employee_id={0}" .format(emp.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(Department.objects.filter(company_id=emp.company_id)),
                          len(response.context["departments"]))
        self.assertEquals(len(Project.objects.filter(company_id=emp.company_id)), len(response.context["projects"]))
        self.assertEquals(len(Role.objects.all()), len(response.context["roles"]))

        form = response.context["form"]
        self.assertEquals(form.initial["employee_id"], emp.id)
        self.assertEquals(form.initial["employeeRole_id"], 0)
        self.assertTrue("department_id" not in form.initial)
        self.assertTrue("project_id" not in form.initial)
        self.assertTrue("role_id" not in form.initial)

    def test_get_form_user_ok(self):
        """
        With proper roles, get the role edit form for an employee
        """
        c = Client()
        c.login(username="emp1", password="123456")
        emp = Employee.objects.get(identifier="emp02")
        response = c.get("/roles/manage?employee_id={0}" .format(emp.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(1, len(response.context["departments"]))
        self.assertEquals(1, len(response.context["projects"]))
        self.assertEquals(len(Role.objects.all()), len(response.context["roles"]))

        self.assertEquals(response.context["departments"][0], Department.objects.get(name="departamento 1"))
        self.assertEquals(response.context["projects"][0], Project.objects.get(name="proyecto 1"))

        form = response.context["form"]
        self.assertEquals(form.initial["employee_id"], emp.id)
        self.assertEquals(form.initial["employeeRole_id"], 0)
        self.assertTrue("department_id" not in form.initial)
        self.assertTrue("project_id" not in form.initial)
        self.assertTrue("role_id" not in form.initial)

    def test_get_form_existing_role_positive(self):
        """
        With proper roles, edit the role of an employee
        """
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)
        response = c.get("/roles/manage?role_id={0}" .format(role.id))

        form = response.context["form"]
        self.assertEquals(form.initial["employee_id"], role.employee_id.id)
        self.assertEquals(form.initial["employeeRole_id"], role.id)
        self.assertEquals(form.initial["department_id"], role.projectDepartment_id.department_id.id)
        self.assertEquals(form.initial["project_id"], role.projectDepartment_id.project_id.id)
        self.assertEquals(form.initial["role_id"], role.role_id.id)

    def test_get_form_existing_role_404(self):
        """
        With proper roles, try editing  an inexistent role
        """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/roles/manage?role_id=99999")
        self.assertEquals(response.status_code, 404)

    def test_get_form_existing_user_404(self):
        """
        With proper roles, try editing the role of an inexistent employee
        """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/roles/manage?employee_id=9999")
        self.assertEquals(response.status_code, 404)

    def test_post_new_role_admin_positive(self):
        """
        As an admin, add a new role to an employee
        """
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 2")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="PROJECT_MANAGER")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertRedirects(response, "/employee/view/{0}/" .format(employee.user.username),
                             fetch_redirect_response=False)

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before + 1, employeeroles_after)

        # Check that the role has been successfully created
        try:
            ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, role_id=role,
                                                      projectDepartment_id__project_id=project,
                                                      projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            self.fail("The role was not successfully created")

    def test_post_new_role_user_positive(self):
        """
        With proper roles, add a new role to an employee
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="COORDINATOR")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertRedirects(response, "/employee/view/{0}/".format(employee.user.username),
                             fetch_redirect_response=False)

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before + 1, employeeroles_after)

        # Check that the role has been successfully created
        try:
            ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, role_id=role,
                                                      projectDepartment_id__project_id=project,
                                                      projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            self.fail("The role was not successfully created")
    def test_post_new_role_user_async_positive(self):
        """
        With proper roles, add a new role to an employee
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="COORDINATOR")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manageAsync", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code,200)
        
        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before + 1, employeeroles_after)

        # Check that the role has been successfully created
        try:
            ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, role_id=role,
                                                      projectDepartment_id__project_id=project,
                                                      projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            self.fail("The role was not successfully created")

    def test_post_new_role_user_form_not_valid(self):
        """
        Try adding a role to an employee when missing params
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="COORDINATOR")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()
        #falta el employeeRole_id
        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'role_id': role.id,
        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the proper error is passed
        self.assertTrue(response.status_code == 200)
        self.assertTrue('roleCreation_formNotValid' in response.context["errors"])

    def test_post_new_role_user_emp_not_existent(self):
        """
        Try adding a role to an employee when you do not have permissions for that project-department pair
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="COORDINATOR")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': 0,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,

        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the proper error is passed
        self.assertTrue(response.status_code == 404)


    def test_post_new_role_user_projdept_not_allowed(self):
        """
        Try adding a role to an employee when you do not have permissions for that project-department pair
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 2")
        role = Role.objects.get(name="COORDINATOR")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the proper error is passed
        self.assertTrue('roleCreation_notAuthorizedProjectDepartment' in response.context["errors"])

    def test_post_new_role_user_role_not_allowed(self):
        """
        Try adding a role to an employee when you cannot assign that role
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="TEAM_MANAGER")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the proper error is passed
        self.assertTrue('roleCreation_notAuthorizedRole' in response.context["errors"])

    def test_post_new_role_admin_duplicated(self):
        """
        Try adding a duplicate role for an user
        """

        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="TEAM_MANAGER")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the proper error is passed
        self.assertTrue('roleCreation_alreadyExists' in response.context["errors"])

    def test_edit_role_above_current_user(self):
        """
        Try adding a role to an employee when your role is lower than which you are trying to assign
        """

        c = Client()
        c.login(username="emp3", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="EMPLOYEE")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        cur_role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': cur_role.id,
            'role_id': role.id,
        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the proper error is passed
        self.assertTrue('roleCreation_editingHigherRole' in response.context["errors"])

    def test_edit_role_positive(self):
        """
        Edit a role successfully
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp03")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="EMPLOYEE")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        cur_role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': cur_role.id,
            'role_id': role.id,
        })

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        self.assertRedirects(response, "/employee/view/{0}/" .format(employee.user.username),
                             fetch_redirect_response=False)

        try:
            ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, role_id=role,
                                                      projectDepartment_id__project_id=project,
                                                      projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            self.fail("The role was not successfully created")

    def test_error_codes_404(self):
        """
        Forces all types of errores in each case
        """
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="EMPLOYEE")
        cur_role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)

        errors = ['departmentDoesNotExist', 'projectDoesNotExist', 'employeeRoleDoesNotExist', 'roleDoesNotExist']

        for i in range(4):
            response = c.post("/roles/manage", {
                'employee_id': employee.id,
                'department_id': department.id if i != 0 else 9999,
                'project_id': project.id if i != 1 else 9999,
                'employeeRole_id': cur_role.id if i != 2 else 9999,
                'role_id': role.id if i != 3 else 9999,
            })

            self.assertTrue(response.status_code == 200)
            self.assertTrue(len(response.context["errors"]) == 1)
            self.assertTrue('roleCreation_' + errors[i] in response.context["errors"])

    def test_delete_role_user_negative(self):
        """
        Try deleting a role you have no permissions to access
        """
        c = Client()
        c.login(username="emp3", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)
        response = c.get("/roles/delete/{0}/" .format(role.id))

        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(employeeroles_before, employeeroles_after)
        self.assertTrue(response.status_code == 403)

    def test_delete_role_user_positive(self):
        """
        Delete a role from an employee successfully
        """
        c = Client()
        c.login(username="emp1", password="123456")

        employee = Employee.objects.get(identifier="emp03")
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)
        response = c.get("/roles/delete/{0}/" .format(role.id))

        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(employeeroles_before, employeeroles_after + 1)
        self.assertRedirects(response, "/employee/view/{0}" .format(employee.user.username),
                             fetch_redirect_response=False)
