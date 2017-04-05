from django.contrib.auth.models                       import User
from django.test                                      import TestCase, Client
from django.core.exceptions                           import ObjectDoesNotExist, PermissionDenied


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
from django.db                                        import transaction
import string, random, json
from datetime                                           import date, timedelta,datetime
from django.utils import timezone

def ranstr():
    # Returns a 10-character random string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

### Métodos para crear objetos
def createDepartments(company):
     Department.objects.create(
        name=ranstr(),
        active=True,
        company_id=company
    )
def createProjects(company):
     Project.objects.create(name=ranstr(), deleted=False, company_id=company)

def createEmployeeInProjDept(project, department,company):
    """
    creates an employee and assigns him/her a new role
    """
    user = User.objects.create_user(
        username=ranstr(),
        password="metronus",
        email=ranstr() + "@metronus.es",
        first_name=ranstr(),
        last_name=ranstr()
    )

    employee = Employee.objects.create(
        user=user,
        user_type="E",
        identifier=ranstr(),
        phone="123123123",
        company_id=company
    )

    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)

    role = Role.objects.get(tier=random.choice([10, 20, 30, 40, 50]))
    ProjectDepartmentEmployeeRole.objects.create(projectDepartment_id=pd, role_id=role, employee_id=employee)

    return employee

def createTaskInProjDept(project, department,admin,rDate):

    try:
        pd = ProjectDepartment.objects.get(project_id=project, department_id=department)
    except ObjectDoesNotExist:
        pd = ProjectDepartment.objects.create(project_id=project, department_id=department)
    measure = random.choice([True, True, True, False]) # Make the task have a 25% chance of not having a production goal

    if measure:
        pgoal=random.uniform(1,100)
        pdescription=ranstr()
    else:
        pgoal=None
        pdescription=""
    task=Task.objects.create(
        name = ranstr(),
        description = ranstr(),
        actor_id = admin,
        production_goal=pgoal,
        goal_description=pdescription,
        projectDepartment_id = pd
    )
    Task.objects.filter(pk=task.id).update(registryDate = rDate.strftime('%Y-%m-%d')+" 10:00+00:00")
    
    #Generate random number of previous goals
    if measure:
        for _ in range(random.randint(1,7)):
            createGoalEvolution(task,admin,rDate)

def createGoalEvolution(task,actor,rDate):
    """
    rDate is the task registryDate, so we will create a date before that
    """
    ge1=GoalEvolution.objects.create(
        task_id=task,
        actor_id = actor,
        production_goal=random.uniform(1,100),
        goal_description=ranstr()
        )
    #get a date before the last task update
    date = rDate - timedelta(days=random.randint(2,30))

    GoalEvolution.objects.filter(pk=ge1.id).update(registryDate = date.strftime('%Y-%m-%d')+" 10:00+00:00")
    
def createTimelogInTask(task, duration, date, employee):
    if task.production_goal is not None and task.production_goal !="":
        punits=random.uniform(1,1000)
    else:
        punits=None
    TimeLog.objects.create(
        description = ranstr(),
        workDate = date,
        duration = duration,
        task_id = task,
        produced_units=punits,
        employee_id = employee
    )

################################## Party hard a partir de aquí ##################################
@transaction.atomic
def randomLoad():
    populate_roles()
    #create company
    company=Company.objects.create(cif="A00000002", company_name="metronus", short_name="metronus", email="info@metronus.es", phone="123456789")
    #From company:metronus: admin
    adminuser=User.objects.create_user(
        username="metronus",
        password="metronus",
        email="admin2@gmail.com",
        first_name="admin2",
        last_name="admin2")
    
    admin=Administrator.objects.create(
        user=adminuser,
        user_type="A",
        identifier="12345",
        phone="123456789",
        company_id=company)
    #create departments
    for _ in range(random.randint(4,8)):
        createDepartments(company)
    #create projects
    for _ in range(random.randint(3,7)):
        createProjects(company)

    #get projects and departments
    departments = list(Department.objects.filter(company_id=company,active=True))
    projects = list(Project.objects.filter(company_id=company,deleted=False))

    #Get all dates between in a month
    dates=[]
    d1 = timezone.now()
    
    for i in range(30):
        dates.append((d1 - timedelta(days=i)))
 
    for i in range(len(departments)-1):
        dpmt = departments[i]
        for j in range(len(projects)-1):
            project=projects[i]
            # Create between 1 and 7 employees for each department and project
            for _ in range(random.randint(2,7)):
                createEmployeeInProjDept(project, dpmt,company)
            # Create between 1 and 4 tasks for each department
            for _ in range(random.randint(1,4)):

                createTaskInProjDept(project, dpmt,admin,random.choice(dates))


            # Create between 1 and 20 timelogs for each task
            for _ in range(random.randint(1,20)):
                duration = random.randint(1,100)
                task = random.choice(Task.objects.filter(projectDepartment_id__project_id = project, projectDepartment_id__department_id = dpmt))
                
                date = random.choice(dates)
                employee=random.choice(Employee.objects.filter(projectdepartmentemployeerole__projectDepartment_id__project_id=project,
                        projectdepartmentemployeerole__projectDepartment_id__department_id=dpmt))
                if employee is not None:
                    createTimelogInTask(task, duration, date,employee)



def populate_roles():
    # El gerente
    Role.objects.create(name="EXECUTIVE", tier=50)
    # El jefe de proyecto
    Role.objects.create(name="PROJECT_MANAGER", tier=40)
    # El jefe de equipo 
    Role.objects.create(name="TEAM_MANAGER", tier=30)
    # El coordinador del departamento
    Role.objects.create(name="COORDINATOR", tier=20)
    # El empleado
    Role.objects.create(name="EMPLOYEE", tier=10)