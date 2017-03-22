from metronus_app.model.company import Company
from metronus_app.model.employee import Employee
from django.contrib.auth.models import User
from metronus_app.model.administrator import Administrator

from django.test import Client
from django.test import TestCase


class LoginTestCase(TestCase):
    def setUp(self):
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

    def test_login_employee(self):
        """
        checks if the employee is logged properly
        """
        c = Client()
        Employee.objects.get(user__username="employee")
        response = c.login(username='employee', password='employee')
        self.assertTrue(response)

    def test_login_admin(self):
        """
        checks if the admin is logged properly
        """
        c = Client()
        Administrator.objects.get(user__username="admin")
        response = c.login(username='admin', password='admin')
        self.assertTrue(response)
