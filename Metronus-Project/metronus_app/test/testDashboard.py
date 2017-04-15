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
        
import string, random
from populate_database import populate_database
def ranstr():
    # Returns a 10-character random string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

class DashboardTestCase(TestCase):
    """This class provides a test case for metrics provided by the dashboard to an administrator"""
    @classmethod
    def setUpTestData(cls):
        populate_database()
    def test_random_data_timeperproject(self):

        def createTimelogInTask(task, duration, date):

            TimeLog.objects.create(
                description = ranstr(),
                workDate = date,
                duration = duration,
                task_id = task,
                employee_id = Employee.objects.get(user__username="anddonram")
            )

        def createTaskInProjDept(project, department):

            try:
                pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
            except ObjectDoesNotExist:
                pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

            Task.objects.create(
                name = ranstr(),
                description = ranstr(),
                actor_id = Administrator.objects.get(user__username="metronus"),
                projectDepartment_id = pd
            )

        c = Client()
        c.login(username="metronus", password="metronus")

        departments = Department.objects.filter(company_id__company_name="metronus")
        projects = Project.objects.filter(company_id__company_name="metronus")

        n_dep=len(departments)
        n_pro=len(projects)
        # Do the random test 5 times

        for k in range(5):

            # Remove all tasks and time logs
            TimeLog.objects.all().delete()
            Task.objects.all().delete()

            true_data = {}

            for i in range(n_pro):
                project=projects[i];

                # Initialize the true data for this department
                true_data[str(project.id)] = {'name': project.name, 'time': 0}

                for i in range(n_dep):
                    dpmt = departments[i]

                    # Create between 1 and 4 tasks for each department
                    for _ in range(random.randint(1,4)):
                        createTaskInProjDept(project, dpmt)


                    # Create between 1 and 10 timelogs for each department
                    for _ in range(random.randint(1,10)):
                        duration = random.randint(1,100)
                        task = random.choice(Task.objects.filter(projectDepartment_id__project_id = project, projectDepartment_id__department_id = dpmt))
                        measure = random.choice([True, True, True, False]) # Make the timelogs have a 25% chance of not being counted towards the metric
                        date = "2016-06-01 10:00+00:00" if measure else "2014-05-01 21:00+00:00"

                        createTimelogInTask(task, duration, date)

                        if measure:
                            true_data[str(project.id)]["time"] += duration

                # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/dashboard/ajaxTimePerProject?start_date=2016-01-01&end_date=2017-01-01" )
            self.assertEquals(response.status_code, 200)
            self.assertJSONEqual(str(response.content, encoding='utf8'), true_data)

