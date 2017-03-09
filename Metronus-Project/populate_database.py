from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.contrib.auth.models import User
from metronus_app.model.administrator import Administrator


def basicLoad():
    Company.objects.create(cif="123", company_name="company1", short_name="company1", email="company1@gmail.com", phone="123456789")
    Company.objects.create(cif="000000000", company_name="metronus", short_name="met", email="metronus@us.com", phone="123456789")
    company = Company.objects.get(cif="123")
    company2 = Company.objects.get(cif="000000000")
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
        username="admin2",
        password="admin2",
        email="admin2@gmail.com",
        first_name="admin2",
        last_name="admin2")
    admin2 = User.objects.get(username="admin2")
    Administrator.objects.create(
        user=admin2,
        user_type="A",
        identifier="12345",
        phone="123456789",
        company_id=company2)

    create_user("anddonram",company2)
    create_user("raisans_138",company2)
    create_user("JoseGavilan",company2)
    create_user("ddlsb",company2)
    create_user("agubelu",company2)
    create_user("JkLiebana",company2)
    create_user("Guardsoul",company2)
    create_user("Barrelito",company2)
    create_user("andjimrio",company2)
    create_user("Jarvie",company2)
    Department.objects.create(name="dep3",active=True,company_id=company)
    Project.objects.create(name="TestProject",deleted=False,company_id=company)

def create_user(nombre,company2):
    User.objects.create_user(
        username=nombre,
        password=nombre,
        email=nombre+"@gmail.com",
        first_name=nombre,
        last_name=nombre)
    user2 = User.objects.get(username=nombre)
    Employee.objects.create(
        user=user2,
        user_type="E",
        identifier="12345",
        phone="123456789",
        company_id=company2)

def populate_roles():
    print("==== POPULATING ROLES ====")
    Role.objects.create(name="Administrator")
    Role.objects.create(name="Project manager")
    Role.objects.create(name="Department manager")
    Role.objects.create(name="Coordinator")
    Role.objects.create(name="Team manager")
    Role.objects.create(name="Employee")
    print("==== %d ROLES INSERTED ====" % Role.objects.all().count())

#############################################################################
#############################################################################
#############################################################################

def populate_database():
    basicLoad()
    populate_roles()
