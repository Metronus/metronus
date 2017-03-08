from metronus_app.model.role import Role
from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from metronus_app.model.project import Project
from metronus_app.model.department import Department
from django.contrib.auth.models import User
from metronus_app.model.administrator import Administrator


def basicLoad():
    Company.objects.create(cif="123", company_name="company1", short_name="company1", email="company1@gmail.com", phone="123456789")
    company = Company.objects.get(cif="123")
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
    Department.objects.create(name="dep3",active=True,company_id=company)
    Project.objects.create(name="TestProject",deleted=False,company_id=company)


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