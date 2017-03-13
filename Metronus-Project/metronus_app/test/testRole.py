from django.test                                      import TestCase, Client
from django.core.exceptions                           import ObjectDoesNotExist

from metronus_app.model.employee                      import Employee
from metronus_app.model.role                          import Role
from metronus_app.model.company                       import Company
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
from metronus_app.model.administrator                 import Administrator
from django.contrib.auth.models                       import User
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from metronus_app.model.projectDepartment             import ProjectDepartment
from metronus_app.forms.roleManagementForm            import RoleManagementForm


class RoleTestCase(TestCase):

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

        project1 = Project.objects.create(
            company_id=company1,
            name="proyecto 1",
        )

        project2 = Project.objects.create(
            company_id=company1,
            name="proyecto 2",
        )

        project3 = Project.objects.create(
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

        department3 = Department.objects.create(
            company_id=company2,
            name="departamento 3",
        )

        projdept1 = ProjectDepartment.objects.create(
            project_id=project1,
            department_id=department1
        )

        projdept2 = ProjectDepartment.objects.create(
            project_id=project1,
            department_id=department2
        )

        projdept3 = ProjectDepartment.objects.create(
            project_id=project2,
            department_id=department1
        )

        role1 = Role.objects.create(name="Administrator")
        role2 = Role.objects.create(name="Project manager")
        role3 = Role.objects.create(name="Department manager")
        role4 = Role.objects.create(name="Coordinator")
        role5 = Role.objects.create(name="Team manager")
        role6 = Role.objects.create(name="Employee")

        emprole1 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=projdept1,
            employee_id=employee1,
            role_id=role2,
        )

        # This one shouldn't happen because the employee is not in the same company as the project,
        # but it's just for testing purposes.
        emprole2 = ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=projdept1,
            employee_id=employee2,
            role_id=role3,
        )

    def test_get_form_without_admin(self):
        c = Client()
        response = c.get("/roles/manage")
        self.assertEquals(response.status_code, 403)

    def test_get_form_without_params(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/roles/manage")
        self.assertEquals(response.status_code, 400)

    def test_get_form_not_existing_employee(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/roles/manage?employee_id=99999")
        self.assertEquals(response.status_code, 404)

    def test_get_form_not_existing_role(self):
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/roles/manage?role_id=99999")
        self.assertEquals(response.status_code, 404)

    def test_get_form_not_allowed_employee(self):
        c = Client()
        c.login(username="admin1", password="123456")
        emp = Employee.objects.get(identifier="emp02")
        response = c.get("/roles/manage?employee_id=%d" % emp.id)
        self.assertEquals(response.status_code, 403)

    def test_get_form_not_allowed_role(self):
        c = Client()
        c.login(username="admin1", password="123456")
        role = ProjectDepartmentEmployeeRole.objects.get(employee_id=Employee.objects.get(identifier="emp02"))
        response = c.get("/roles/manage?role_id=%d" % role.id)
        self.assertEquals(response.status_code, 403)


    def test_get_form_new_role_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        response = c.get("/roles/manage?employee_id=%d" % employee.id)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(Department.objects.filter(company_id=employee.company_id)), len(response.context["departments"]))
        self.assertEquals(len(Project.objects.filter(company_id=employee.company_id)), len(response.context["projects"]))
        self.assertEquals(len(Role.objects.all()), len(response.context["roles"]))

        form = response.context["form"]
        self.assertEquals(form.initial["employee_id"], employee.id)
        self.assertEquals(form.initial["employeeRole_id"], 0)
        self.assertTrue("department_id" not in form.initial)
        self.assertTrue("project_id" not in form.initial)
        self.assertTrue("role_id" not in form.initial)

    def test_get_form_existing_role_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        role = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee)
        response = c.get("/roles/manage?role_id=%d" % role.id)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(Department.objects.filter(company_id=employee.company_id)), len(response.context["departments"]))
        self.assertEquals(len(Project.objects.filter(company_id=employee.company_id)), len(response.context["projects"]))
        self.assertEquals(len(Role.objects.all()), len(response.context["roles"]))

        form = response.context["form"]
        self.assertEquals(form.initial["employee_id"], role.employee_id.id)
        self.assertEquals(form.initial["employeeRole_id"], role.id)
        self.assertEquals(form.initial["department_id"], role.projectDepartment_id.department_id.id)
        self.assertEquals(form.initial["project_id"], role.projectDepartment_id.project_id.id)
        self.assertEquals(form.initial["role_id"], role.role_id.id)

    def test_post_new_role_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 2")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Department manager")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertRedirects(response, "/employee/view/%s/" % employee.user.username, fetch_redirect_response=False)

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before + 1, employeeroles_after)

        # Check that the role has been successfully created
        try:
            createdrole = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, role_id=role, projectDepartment_id__project_id=project, projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            self.fail("The role was not successfully crated")

    def test_post_new_role_updating_current_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Team manager")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()
        role_before = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, projectDepartment_id__project_id=project, projectDepartment_id__department_id=department).role_id.name

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertRedirects(response, "/employee/view/%s/" % employee.user.username, fetch_redirect_response=False)

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()
        role_after = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, projectDepartment_id__project_id=project, projectDepartment_id__department_id=department).role_id.name

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the role has been successfully updated
        self.assertTrue(role_before != role_after)

    def test_post_existing_role_updating_current_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()
        role_before = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, projectDepartment_id__project_id=project, projectDepartment_id__department_id=department)
        role_name_before = role_before.role_id.name

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': role_before.id,
            'role_id': role.id,
        })

        self.assertRedirects(response, "/employee/view/%s/" % employee.user.username, fetch_redirect_response=False)

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()
        role_name_after = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, projectDepartment_id__project_id=project, projectDepartment_id__department_id=department).role_id.name

        self.assertEquals(projdepts_before, projdepts_after)
        self.assertEquals(employeeroles_before, employeeroles_after)

        # Check that the role has been successfully updated
        self.assertTrue(role_name_before != role_name_after)

    def test_post_existing_role_creating_new_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 2")
        project = Project.objects.get(name="proyecto 2")
        role = Role.objects.get(name="Coordinator")

        old_department = Department.objects.get(name="departamento 1")
        old_project = Project.objects.get(name="proyecto 1")

        projdepts_before = ProjectDepartment.objects.all().count()
        employeeroles_before = ProjectDepartmentEmployeeRole.objects.all().count()
        role_before = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, projectDepartment_id__project_id=old_project, projectDepartment_id__department_id=old_department)
        
        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': role_before.id,
            'role_id': role.id,
        })

        self.assertRedirects(response, "/employee/view/%s/" % employee.user.username, fetch_redirect_response=False)

        projdepts_after = ProjectDepartment.objects.all().count()
        employeeroles_after = ProjectDepartmentEmployeeRole.objects.all().count()
        
        self.assertEquals(projdepts_before + 1, projdepts_after)
        self.assertEquals(employeeroles_before + 1, employeeroles_after)

        # Check that the role has been successfully created
        try:
            createdrole = ProjectDepartmentEmployeeRole.objects.get(employee_id=employee, role_id=role, projectDepartment_id__project_id=project, projectDepartment_id__department_id=department)
        except ObjectDoesNotExist:
            self.fail("The role was not successfully crated")

    def test_post_employee_doesnt_exist(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id + 1000,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code, 404)

    def test_post_department_doesnt_exist(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id + 1000,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code, 404)

    def test_post_project_doesnt_exist(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id + 1000,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code, 404)

    def test_post_role_doesnt_exist(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id+ 1000,
        })

        self.assertEquals(response.status_code, 404)

    def test_post_employee_not_allowed(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp02")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code, 403)

    def test_post_department_not_allowed(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 3")
        project = Project.objects.get(name="proyecto 1")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code, 403)

    def test_post_project_not_allowed(self):
        c = Client()
        c.login(username="admin1", password="123456")

        employee = Employee.objects.get(identifier="emp01")
        department = Department.objects.get(name="departamento 1")
        project = Project.objects.get(name="proyecto 3")
        role = Role.objects.get(name="Coordinator")

        response = c.post("/roles/manage", {
            'employee_id': employee.id,
            'department_id': department.id,
            'project_id': project.id,
            'employeeRole_id': 0,
            'role_id': role.id,
        })

        self.assertEquals(response.status_code, 403)