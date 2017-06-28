from metronus_app.model.department      import Department
from metronus_app.model.task            import Task
from django.test                        import TestCase, Client
from metronus_app.model.project         import Project
from metronus_app.model.goalEvolution   import GoalEvolution
from populate_database                  import populate_database
import json
from django.urls import reverse

class TaskTestCase(TestCase):
    """This class provides a test case for using and managing tasks"""
    @classmethod
    def setUpTestData(cls):
        """
        Loads the data to the database for tests to be done
        """
        populate_database()

    def test_create_task_positive(self):
        """ Logged in as an employee with appropiate role, try to create a task"""
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = Task.objects.all().count()
        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id

        response = c.post("/task/create", {
            "task_id": "0",
            "name": "dep4",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "price_per_hour":6.0
              })

        self.assertEquals(response.status_code, 302)

        # Check that the task has been successfully created

        dep = Task.objects.all().last()
        self.assertEquals(dep.name, "dep4")
        self.assertEquals(dep.active,True)
        logs_after = Task.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_task_positive_2(self):
        """Logged in as an administrator, try to create a task"""
        c = Client()
        c.login(username="metronus", password="metronus")

        logs_before = Task.objects.all().count()
        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id

        response = c.post("/task/createAsync", {
            "task_id": "0",
            "name": "hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "price_per_hour":2.0
              })

        self.assertEquals(response.status_code, 200)

        # Check that the task has been successfully created

        dep = Task.objects.all().last()
        self.assertEquals(dep.name, "hacer memes")
        self.assertEquals(dep.active,True)

        #response in bytes must be decode to string
        data=response.content.decode("utf-8")
        #string to dict
        data=json.loads(data)
        self.assertEquals(data["success"],True)
        logs_after = Task.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_create_invalid_task_filled_price(self):
        """Logged in as an employee with appropiate role, try to create a task
        both fields filled
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = GoalEvolution.objects.all().count()
        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id

        response = c.post("/task/create", {
            "task_id": "0",
            "name": "dep4",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "price_per_hour":6.0,
            "price_per_unit":4.0
              })

        self.assertEquals(response.status_code, 200)
        logs_after = GoalEvolution.objects.all().count()
        self.assertEquals(logs_before, logs_after)
        self.assertNotIn("task_creation_invalid_goal",response.context["errors"])
        self.assertIn("task_creation_invalid_price",response.context["errors"])

    def test_create_task_invalid_goal(self):
        """Logged in as an employee with appropiate role, try to create a task
        both fields filled
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        logs_before = GoalEvolution.objects.all().count()
        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id

        response = c.post("/task/create", {
            "task_id": "0",
            "name": "dep4",
            "project_id":pro_id,
            "department_id":dep_id,
            "price_per_unit":4.0,
            "production_goal":"2.0",
            "description":"alguno",
            "goal_description":""
              })

        self.assertEquals(response.status_code, 200)
        logs_after = GoalEvolution.objects.all().count()
        self.assertEquals(logs_before, logs_after)
        self.assertIn("task_creation_invalid_goal",response.context["errors"])
        self.assertIn("task_creation_invalid_price",response.context["errors"])


    def test_create_task_duplicate(self):
        """
        Logged in as an administrator, try to create an task with the name of an existing company
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        response = c.post("/task/create", {
            "task_id": "0",
            "description":"alguno",
            "name": "Hacer cosas",
            "project_id":str(Project.objects.get(name="Metronus").id),
            "department_id":str(Department.objects.get(name="Backend").id),
            "price_per_hour":"1.0"
        })

        self.assertEquals(response.status_code, 200)
        self.assertIn("task_creation_repeated_name",response.context["errors"])
        self.assertNotIn("task_creation_project_department_not_related",response.context["errors"])

    def test_create_task_project_department_not_related(self):
        """
        Logged in as an administrator, try to create an task with the name of an existing company
        """
        c = Client()
        c.login(username="admin", password="admin")

        response = c.post("/task/create", {
            "task_id": "0",
            "description":"alguno",
            "name": "Hacer cosas",
            "project_id":str(Project.objects.get(name="Proust-Ligeti").id),
            "department_id":str(Department.objects.get(name="dep3").id),
            "price_per_hour":"3.0"
        })
        self.assertEquals(response.status_code, 200)
        self.assertNotIn("task_creation_repeated_name",response.context["errors"])
        self.assertIn("task_creation_project_department_not_related",response.context["errors"])


    def test_create_task_not_logged(self):
        """
        Try creating a task without authentication
        """
        c = Client()
        response = c.get("/task/create")
        self.assertEquals(response.status_code, 403)

    def test_create_task_not_allowed(self):
        """
        Try creating a task without proper roles
        """
        c = Client()
        c.login(username="anddonram", password="123456")
        response = c.get("/task/create")
        self.assertEquals(response.status_code, 403)


    def test_list_tasks_positive(self):
        """
        List tasks according to user roles(Project manager)
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        response = c.get("/task/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["tasks"]), 3)

    def test_list_tasks_positive_2(self):
        """
        List tasks according to user roles(Frontend department)
        """
        c = Client()
        c.login(username="Barrelito", password="123456")
        response = c.get("/task/list")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context["tasks"]), 1)

    def test_list_tasks_not_logged(self):
        """
        Try listing the tasks without authentication
        """
        c = Client()
        response = c.get("/task/list")
        self.assertEquals(response.status_code, 403)

    def test_form_task_positive(self):
            """
            Get task creation form task  with proper roles (Backend department)
            """
            c = Client()
            c.login(username="ddlsb", password="123456")
            
            
            response = c.get("/task/create")
            self.assertEquals(response.status_code, 200)
            form = response.context["form"]
            
            self.assertTrue(form is not None)
            self.assertTrue(response.context["projects"].count()>0)
    def test_form_task_find_departments(self):
            """
            Get task creation form task  with proper roles (Backend department)
            """
            c = Client()
            c.login(username="agubelu", password="123456")
            
            
            response = c.get("/task/getdepartments?project_id={0}".format(Project.objects.get(name="Metronus").id))
            self.assertEquals(response.status_code, 200)
            #response in bytes must be decode to string
            data=response.content.decode("utf-8")
            #string to dict
            data=json.loads(data)
            self.assertTrue(len(data)>0)
            self.assertTrue(data[0]['model'],'metronus_app_department')
            


    def test_view_task_positive(self):
        """
        View task details with proper roles (Backend department)
        """
        c = Client()
        c.login(username="agubelu", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["task"]

        self.assertEquals(form.id, dep_id)
        self.assertEquals(response.context["goal_evolution"]==None,False)

    def test_view_task_negative_2(self):
        """
        Try viewing details without proper roles (Backend employee-Backend task)
        """
        c = Client()
        c.login(username="agubelu", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id
        c.login(username="anddonram", password="123456")
        response = c.get("/task/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_view_task_negative(self):
        """
        Try viewing details without proper roles (Frontend employee - Backend task)
        """
        c = Client()
        c.login(username="agubelu", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id

        c.logout()
        c.login(username="andjimrio", password="123456")
        response = c.get("/task/view/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_edit_task_get(self):
        """
        Get the task edit form with proper roles
        """
        c = Client()
        c.login(username="ddlsb", password="123456")
        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id
        response = c.get("/task/edit/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["task_id"], dep_id)

    def test_edit_task_404(self):
        """
        Try editing inexistent task
        """

        c = Client()
        c.login(username="agubelu", password="123456")

        response = c.get("/task/edit?task_id=9000")
        self.assertEquals(response.status_code, 404)

    def test_edit_task_positive(self):
        """
        Logged in as an administrator, try to edit a task
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        pro_id=Project.objects.get(name="Metronus").id,
        dep_id=Department.objects.get(name="Frontend").id
        task_id=Task.objects.filter(name="Hacer cosas de cua").first().id

        logs_before = GoalEvolution.objects.all().count()

        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "production_goal":"3.0",
            "goal_description":"kgs",
            "price_per_unit":"6.0"
              })

        self.assertEquals(response.status_code, 302)
        logs_after = GoalEvolution.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)

    def test_edit_task_positive_2(self):
        """
        Logged in as an administrator, try to edit a task
        no new entry is created
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id


        task_id=Task.objects.filter(name="Hacer cosas de front").first().id

        logs_before = GoalEvolution.objects.all().count()

        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "production_goal":"2.0",
            "goal_description":"kgs",
            "price_per_unit":"7.0"
              })

        self.assertEquals(response.status_code, 302)
        logs_after = GoalEvolution.objects.all().count()

        self.assertEquals(logs_before, logs_after)

    def test_edit_task_positive_3(self):
        """
        Logged in as an administrator, try to edit a task
        an entry is created with the new price_per_unit
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id


        task_id=Task.objects.filter(name="Hacer cosas de front").first().id

        logs_before = GoalEvolution.objects.all().count()

        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "production_goal":"2.0",
            "goal_description":"kgs",
            "price_per_unit":"4.0"
              })

        self.assertEquals(response.status_code, 302)
        logs_after = GoalEvolution.objects.all().count()

        self.assertEquals(logs_before+1, logs_after)

    def test_edit_task_invalid_price(self):
        """
        Logged in as an administrator, try to edit a task with goal and change its price for per hour
        no new entry is created
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id


        task_id=Task.objects.filter(name="Hacer cosas de front").first().id

        logs_before = GoalEvolution.objects.all().count()

        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "production_goal":"2.0",
            "goal_description":"kgs",
            "price_per_hour":"2.75"
              })

        self.assertEquals(response.status_code, 200)
        logs_after = GoalEvolution.objects.all().count()
        self.assertEquals(logs_before, logs_after)

        self.assertNotIn("task_creation_invalid_goal",response.context["errors"])
        self.assertIn("task_creation_invalid_price",response.context["errors"])

    def test_edit_task_invalid_price_all_filled(self):
        """
        Logged in as an administrator, try to edit a task with goal with both prices filled
        no new entry is created
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id


        task_id=Task.objects.filter(name="Hacer cosas de front").first().id

        logs_before = GoalEvolution.objects.all().count()

        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "production_goal":"2.0",
            "goal_description":"kgs",
            "price_per_hour":"2.75",
            "price_per_unit":"2.75"
              })

        self.assertEquals(response.status_code, 200)
        logs_after = GoalEvolution.objects.all().count()
        self.assertEquals(logs_before, logs_after)
        self.assertNotIn("task_creation_invalid_goal",response.context["errors"])
        self.assertIn("task_creation_invalid_price",response.context["errors"])


    def test_edit_task_invalid_goal(self):
        """
        Logged in as an administrator, try to edit a task
        """
        c = Client()
        c.login(username="metronus", password="metronus")

        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Frontend").id
        response = c.get("/task/list")
        task_id=response.context["tasks"][0].id


        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer memes",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "production_goal":"2.0",
            "goal_description":""
              })

        self.assertEquals(response.status_code, 200)
        self.assertIn("task_creation_invalid_goal",response.context["errors"])
        self.assertIn("task_creation_invalid_price",response.context["errors"])


    def test_edit_task_duplicate(self):
        """
        Logged in as an employee, try to edit a task
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        pro_id=Project.objects.get(name="Metronus").id,

        dep_id=Department.objects.get(name="Backend").id
        response = c.get("/task/list")
        task_id=Task.objects.get(name="Hacer cosas").id
        response = c.post("/task/edit/"+str(task_id)+"/", {
            "task_id": task_id,
            "name": "Hacer cosas de back",
            "description":"alguno",
            "project_id":pro_id,
            "department_id":dep_id,
            "price_per_hour":"8.0"
              })

        self.assertEquals(response.status_code, 200)

        self.assertIn("task_creation_repeated_name",response.context["errors"])

    def test_delete_task_positive(self):
        """
        Delete a task with proper roles
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id

        response = c.get("/task/delete/"+str(dep_id)+"/")
        self.assertRedirects(response, "/task/list", fetch_redirect_response=False)

        self.assertFalse(Task.objects.get(pk=dep_id).active)

    def test_delete_task_not_allowed(self):
        """
        Try deleting a task without proper roles
        """
        c = Client()
        c.login(username="andjimrio", password="123456")
        task=Task.objects.filter(name="Hacer cosas de back").first()
        response = c.get("/task/delete/"+str(task.id)+"/")
        self.assertEquals(response.status_code, 403)

    def test_delete_task_not_active(self):
        """
        Try deleting an already deleted task
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        dep_id=Task.objects.filter(active=False).first().id
        response = c.get("/task/delete/"+str(dep_id)+"/")
        self.assertEquals(response.status_code, 404)

    def test_recover_task_positive(self):
        """
        Delete a task with proper roles
        """
        c = Client()
        c.login(username="ddlsb", password="123456")

        response = c.get("/task/list")
        dep_id=response.context["tasks"][0].id

        response = c.get(reverse("task_delete",args=(dep_id,)))
        self.assertRedirects(response, "/task/list", fetch_redirect_response=False)

        self.assertFalse(Task.objects.get(pk=dep_id).active)


        response = c.get(reverse("task_recover",args=(dep_id,)))
        self.assertRedirects(response, "/task/list", fetch_redirect_response=False)

        self.assertTrue(Task.objects.get(pk=dep_id).active)
