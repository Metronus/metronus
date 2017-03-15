from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.contrib.auth.models import User
from metronus_app.model.administrator import Administrator
from metronus_app.model.task import Task
from metronus_app.model.projectDepartment import ProjectDepartment
from metronus_app.model.projectDepartmentEmployeeRole import ProjectDepartmentEmployeeRole
from django.db import transaction

@transaction.atomic
def basicLoad():
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
        company_id=company)

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

    emp_role=Role.objects.get(name="Employee")
    coor_role=Role.objects.get(name="Coordinator")
    pm_role=Role.objects.get(name="Project manager")

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

    ProjectDepartmentEmployeeRole.objects.create(
        projectDepartment_id=pd1,
        employee_id=emp4,
        role_id=Role.objects.get(name="Administrator") )

    Task.objects.create(
        name  ="Hacer cosas",
        description  = "meda",
        actor_id = emp4,
        projectDepartment_id = pd1
    )

    Task.objects.create(
        name  ="Hacer cosas de back",
        description  = "hola",
        actor_id = emp5,
        projectDepartment_id = pd1
    )
    Task.objects.create(
        name  ="Hacer cosas de front",
        description  = "nada",
        actor_id = emp8,
        projectDepartment_id = pd2
    )
    Task.objects.create(
        name  ="Hacer cosas de cua",
        description  = "nada",
        actor_id = emp8,
        projectDepartment_id = pd1,
        active=False
    )
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
    Role.objects.create(name="Administrator")
    Role.objects.create(name="Project manager")
    Role.objects.create(name="Department manager")
    Role.objects.create(name="Coordinator")
    Role.objects.create(name="Team manager")
    Role.objects.create(name="Employee")

#############################################################################
#############################################################################
#############################################################################

def populate_database():
    basicLoad()
