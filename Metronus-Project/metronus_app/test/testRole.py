from django.test import TestCase

from metronus_app.model.employee                      import Employee
from metronus_app.model.role                          import Role
from metronus_app.model.company                       import Company
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
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

        department1 = Department.objects.create(
            company_id=company1,
            name="departamento 1",
        )

        department2 = Department.objects.create(
            company_id=company1,
            name="departamento 2",
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