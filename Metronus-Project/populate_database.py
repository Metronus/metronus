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
@transaction.atomic
def basic_load():
    """
    Loads a lot of data from scratch
    """
    company=Company.objects.create(cif="A00000001", company_name="company1", short_name="company1", email="company1@gmail.com", phone="123456789")
    company2=Company.objects.create(cif="A00000002", company_name="metronus", short_name="metronus", email="info@metronus.es", phone="123456789")
    #From first company:company1
    User.objects.create_user(
        username="employee",
        password="employee",
        email="employee@gmail.com",
        first_name="employee",
        last_name="employee")
    user = User.objects.get(username="employee")
    Employee.objects.create(
        user=user,
        user_type="E",
        identifier="12345",
        phone="123456789",
        company_id=company,
        price_per_hour=2.0)

    User.objects.create_user(
        username="admin",
        password="admin",
        email="admin@gmail.com",
        first_name="admin",
        last_name="admin")
    admin = User.objects.get(username="admin")
    Administrator.objects.create(
        user=admin,
        user_type="A",
        identifier="12345",
        phone="123456789",
        company_id=company)

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
    emp2=create_user("raisans_138",company2)
    emp3=create_user("JoseGavilan",company2)
    emp4=create_user("ddlsb",company2)
    emp5=create_user("agubelu",company2)
    emp6=create_user("JkLiebana",company2)
    emp7=create_user("Guardsoul",company2)
    emp8=create_user("Barrelito",company2)
    emp9=create_user("andjimrio",company2)
    emp10=create_user("Jarvie",company2)
    Department.objects.create(name="dep3",active=True,company_id=company)
    Project.objects.create(name="TestProject",deleted=False,company_id=company)

    proj1 = Project.objects.create(
        name="Metronus",
        deleted=False,
        company_id=company2)

    proj2 = Project.objects.create(
        name="Proust-Ligeti",
        deleted=False,
        company_id=company)

    dep1 = Department.objects.create(
        name="Backend",
		active=True,company_id=company2)

    dep2 = Department.objects.create(
        name="Frontend",
		active=True,
		company_id=company2)

    #Frontend
    pd1 = ProjectDepartment.objects.create(
		project_id = proj1,
		department_id = dep1)

    #Backend
    pd2 = ProjectDepartment.objects.create(
		project_id = proj1,
		department_id = dep2)

    populate_roles()

    emp_role=Role.objects.get(name="EMPLOYEE")
    coor_role=Role.objects.get(name="COORDINATOR")
    pm_role=Role.objects.get(name="PROJECT_MANAGER")
    team_role=Role.objects.get(name="TEAM_MANAGER")

    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp1,
        role_id= emp_role)
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp2,
        role_id=emp_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd2,
        employee_id=emp3,
        role_id=emp_role )

    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp4,
        role_id=pm_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd2,
        employee_id=emp4,
        role_id=pm_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd2,
        employee_id=emp4,
        role_id=team_role )

    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp5,
        role_id=coor_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd2,
        employee_id=emp6,
        role_id= emp_role)
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp7,
        role_id=emp_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd2,
        employee_id=emp8,
        role_id=coor_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd2,
        employee_id=emp9,
        role_id=emp_role )
    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp10,
        role_id=emp_role )


    task1 = Task.objects.create(
        name  ="Hacer cosas",
        description  = "meda",
        actor_id = emp4,
        projectDepartment_id = pd1,
        price_per_hour=1.0
    )

    task2 = Task.objects.create(
        name  ="Hacer cosas de back",
        description  = "hola",
        actor_id = emp5,
        projectDepartment_id = pd1,
        price_per_hour=7.0
    )

    task3 = Task.objects.create(
        name  ="Hacer cosas de front",
        description  = "nada",
        actor_id = emp8,
        projectDepartment_id = pd2,
        production_goal="2.0",
        goal_description="kgs",
        price_per_unit=7.0
    )

    task4 = Task.objects.create(
        name  ="Hacer cosas de cua",
        description  = "nada",
        actor_id = emp8,
        projectDepartment_id = pd1,
        active=False,
        price_per_hour=3.0
    )

    TimeLog.objects.create(
        description = "he currado mucho",
        workDate = "2017-01-02 10:00+00:00",
        duration = 240,
        task_id = task1,
        employee_id = emp4
    )

    TimeLog.objects.create(
        description = "he currado poco",
        workDate = "2017-03-20 13:37+00:00",
        duration = 60,
        task_id = task1,
        employee_id = emp3
    )

    TimeLog.objects.create(
        description = "me quiero morir",
        workDate = "2017-02-12 15:30+00:00",
        duration = 400,
        task_id = task1,
        employee_id = emp3
    )

    TimeLog.objects.create(
        description = "me quiero morir mas que nunca",
        workDate = "2017-02-14 15:30+00:00",
        duration = 400,
        task_id = task3,
        produced_units="1.5",
        employee_id = emp3
    )

    TimeLog.objects.create(
        description = "me quiero morir algunos dias",
        workDate = "2017-04-01 15:30+00:00",
        duration = 300,
        task_id = task3,
        produced_units="0.5",
        employee_id = emp4
    )

    TimeLog.objects.create(
        description = "me quiero morir",
        workDate = "2017-02-12 15:30+00:00",
        duration = 400,
        task_id = task3,
        produced_units="8",
        employee_id = emp3
    )
    ge1=GoalEvolution.objects.create(
        task_id=task3,

        actor_id = emp8,
        production_goal=9.0,
        goal_description="kgs",
        price_per_unit=3.0
        )

    ge2=GoalEvolution.objects.create(
        task_id=task3,

        actor_id = emp8,
        production_goal=4.0,
        goal_description="kgs",
        price_per_unit=2.0
        )
    #as registryDate is an autofield_now and updates on save(), we must set the registrydate with update()
    #if we want to force a date in registryDate
    GoalEvolution.objects.filter(pk=ge1.id).update(registryDate = "2017-02-11 15:30+00:00")
    GoalEvolution.objects.filter(pk=ge2.id).update(registryDate = "2017-02-13 15:30+00:00")
    Task.objects.filter(pk=task3.id).update(registryDate = "2017-02-13 16:30+00:00")
def create_user(nombre,company2):
    User.objects.create_user(
        username=nombre,
        password="123456",
        email=nombre+"@gmail.com",
        first_name=nombre,
        last_name=nombre)
    user2 = User.objects.get(username=nombre)
    return Employee.objects.create(
        user=user2,
        user_type="E",
        identifier="12345",
        phone="123456789",
        company_id=company2)

def populate_roles():
    """
    Loads... the available roles!!
    """
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

#############################################################################
#############################################################################
#############################################################################
def populate_database():
    """
    This is called by python3 manage.py populate
    """
    basic_load()
