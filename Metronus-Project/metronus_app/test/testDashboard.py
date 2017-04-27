from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist

from metronus_app.model.employee import Employee
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.task import Task
from metronus_app.model.timeLog import TimeLog
from metronus_app.model.project import Project
from metronus_app.model.administrator import Administrator
from metronus_app.model.department import Department
from metronus_app.common_utils import  ranstr,create_timelog_in_task,create_task_in_projdept
import random
from populate_database import populate_database


class DashboardTestCase(TestCase):
    """This class provides a test case for metrics provided by the dashboard to an administrator"""
    @classmethod
    def setUpTestData(cls):
        """
        Loads the data to the database for tests to be done
        """
        populate_database()
    def test_view(self):
        """
        Shows the main view
        """
        c = Client()
        c.login(username="metronus", password="metronus")
        response = c.get("/dashboard/view")
        self.assertEquals(response.status_code, 200)

    def test_view_negative(self):
            """
            Shows the main view... or not because it is not an admin
            """
            c = Client()
            c.login(username="ddlsb", password="123456")
            response = c.get("/dashboard/view")
            self.assertEquals(response.status_code, 403)

    def test_random_data_timeperproject(self):
        """
        Does a lot of random test,thus ensuring the dashboard provides the correct data every time
        """

        admin=Administrator.objects.get(user__username="metronus")
        emp=Employee.objects.get(user__username="anddonram")
        c = Client()
        c.login(username="metronus", password="metronus")

        departments = Department.objects.filter(company_id__company_name="metronus")
        projects = Project.objects.filter(company_id__company_name="metronus")

        n_dep = len(departments)
        n_pro = len(projects)
        # Do the random test 5 times

        for _ in range(5):

            # Remove all tasks and time logs
            TimeLog.objects.all().delete()
            Task.objects.all().delete()

            true_data = {}

            for i in range(n_pro):
                project = projects[i]

                # Initialize the true data for this department
                true_data[str(project.id)] = {'name': project.name, 'time': 0}

                for j in range(n_dep):
                    dpmt = departments[j]

                    # Create between 1 and 4 tasks for each department
                    for _ in range(random.randint(1, 4)):
                        create_task_in_projdept(project, dpmt,admin)

                    # Create between 1 and 10 timelogs for each department
                    for _ in range(random.randint(1, 10)):
                        duration = random.randint(1, 100)
                        task = random.choice(Task.objects.filter(projectDepartment_id__project_id=project, projectDepartment_id__department_id=dpmt))
                        measure = random.choice([True, True, True, False])  # Make the timelogs have a 25% chance of not being counted towards the metric
                        date = "2016-06-01 10:00+00:00" if measure else "2014-05-01 21:00+00:00"

                        create_timelog_in_task(task, duration, date,emp)

                        if measure:
                            true_data[str(project.id)]["time"] += duration

                # Check that the data returned by the AJAX query matches the generated data

            response = c.get("/dashboard/ajaxTimePerProject?start_date=2016-01-01&end_date=2017-01-01")
            self.assertEquals(response.status_code, 200)
            self.assertJSONEqual(str(response.content, encoding='utf8'), true_data)

    def test_timeperproject_bad_start_date(self):
        """
        Request the timeperproject with a wrong start date
        """

        c = Client()
        c.login(username="metronus", password="metronus")

        response = c.get("/dashboard/ajaxTimePerProject?start_date=20101-01&end_date=2017-01-01")
        self.assertEquals(response.status_code, 400)

    def test_timeperproject_bad_end_date(self):
        """
        Request the timeperproject with a wrong end date
        """

        c = Client()
        c.login(username="metronus", password="metronus")

        response = c.get("/dashboard/ajaxTimePerProject?start_date=2016-01-01&end_date=20101-01")
        self.assertEquals(response.status_code, 400)
           
    def test_timeperproject_bad_end_offset(self):
        """
        Request the timeperproject with a wrong offset
        """

        c = Client()
        c.login(username="metronus", password="metronus")

        response = c.get("/dashboard/ajaxTimePerProject?offset=+53:20")
        self.assertEquals(response.status_code, 400)
          
    def test_access_ok_employees_per_project(self):
        """
        Get the ajaxEmployeesPerProject metric as an admin
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        response = c.get("/dashboard/ajaxEmployeesPerProject")
        self.assertEquals(response.status_code, 200)

    def test_access_ok_departments_per_project(self):
        """
        Get the ajaxDepartmentsPerProject metric as an admin
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        response = c.get("/dashboard/ajaxDepartmentsPerProject")
        self.assertEquals(response.status_code, 200)

    def test_access_ok_tasks_per_project(self):
        """
        Get the ajaxTasksPerProject metric as an admin
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        response = c.get("/dashboard/ajaxTasksPerProject")
        self.assertEquals(response.status_code, 200)
