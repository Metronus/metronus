from metronus_app.model.role                          import Role
from metronus_app.model.company                       import Company
from metronus_app.model.employee                      import Employee
from metronus_app.model.project                       import Project
from metronus_app.model.department                    import Department
from django.contrib.auth.models                       import User
from metronus_app.model.administrator                 import Administrator
from metronus_app.model.task                          import Task
from metronus_app.model.timeLog                       import TimeLog
from metronus_app.model.projectDepartment             import ProjectDepartment
from metronus_app.model.goalEvolution             import GoalEvolution
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.test                        import TestCase

from populate_database import create_user
class ModelStringTestCase(TestCase):
    """This class provides a test for the string format for each model class. You know..."""
    @classmethod
    def setUpTestData(cls):
        """
        Loads the data to the database for tests to be done
        """
        company2=Company.objects.create(cif="A00000002", company_name="metronus", short_name="metronus", email="info@metronus.es", phone="123456789")

        #From second company:metronus
        User.objects.create_user(
            username="metronus",
            password="metronus",
            email="admin2@gmail.com",
            first_name="admin2",
            last_name="admin2")
        admin2 = User.objects.get(username="metronus")
        Administrator.objects.create(
            user=admin2,
            user_type="A",
            identifier="12345",
            phone="123456789",
            company_id=company2)

        emp1=create_user("anddonram",company2)
        proj1 = Project.objects.create(
            name="Metronus",
            deleted=False,
            company_id=company2)
        dep1 = Department.objects.create(
            name="Backend",
            active=True,company_id=company2)
        #Frontend
        pd1 = ProjectDepartment.objects.create(
            project_id = proj1,
            department_id = dep1)

        emp_role=Role.objects.create(name="EMPLOYEE", tier=10)

        ProjectDepartmentEmployeeRole.objects.create(
            projectDepartment_id=pd1,
            employee_id=emp1,
            role_id= emp_role)

        task1 = Task.objects.create(
            name  ="Hacer cosas",
            description  = "meda",
            actor_id = emp1,
            projectDepartment_id = pd1,
            price_per_hour=1.0
        )

        TimeLog.objects.create(
            description = "he currado mucho",
            workDate = "2017-01-02 10:00+00:00",
            duration = 240,
            task_id = task1,
            employee_id = emp1
        )
        GoalEvolution.objects.create(
            task_id=task1,

            actor_id = emp1,
            production_goal=9.0,
            goal_description="kgs",
            price_per_unit=3.0
            )

    def test_strings_ok(self):
        """
        Checks the models have a proper string representation
        """
        def do_test(model,string):
            """
            Searches the first and checks equals
            """
            self.assertEquals(model.objects.first().__unicode__(),string)

        do_test(Administrator,"12345")
        do_test(Company,"metronus")
        do_test(Department,"Backend")
        do_test(Employee,"12345")
        do_test(GoalEvolution,9.0)
        do_test(Project,"Metronus")
        do_test(ProjectDepartment,"Backend - Metronus")
        do_test(ProjectDepartmentEmployeeRole,"Backend - Metronus")
        do_test(Role,"EMPLOYEE")
        do_test(Task,"Hacer cosas")
        do_test(TimeLog,"Hacer cosas - 2017-01-02 10:00 - he currado mucho")