from metronus_app.model.company         import Company
from metronus_app.model.administrator   import Administrator
from django.contrib.auth.models         import User
from django.test                        import TestCase, Client
from metronus_app.common_utils          import get_ajax
import json


class CompanyTestCase(TestCase):
    """This class provides a test case for companies signing up to the system"""

    def setUp(self):
        """
        Loads the data to the database for tests to be done
        """
        company1 = Company.objects.create(
            cif="231231F",
            company_name="Universidad de Sevilla",
            short_name="us",
            email="us@gmail.com",
            phone="123456789")

        admin_user = User.objects.create_user(
            username="admin1",
            password="123456",
            email="admin1@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        Administrator.objects.create(
            user=admin_user,
            user_type="A",
            identifier="adm01",
            phone="666555444",
            company_id=company1
        )

    def test_create_company(self):
        """
        checks the number of companies increased
        """
        count1 = Company.objects.count()
        Company.objects.create(
            cif="123",
            company_name="company1",
            short_name="cosa",
            email="company1@gmail.com",
            phone="123456789")
        count2 = Company.objects.count()
        self.assertTrue(count1+1, count2)


    def test_shortname_positive(self):
        """
        Checks if the AJAX method of checking a short name is correct
        """
        cpy = Company.objects.all()[:1].get()
        data = get_ajax("/ajax/validate_short_name/", {'short_name' : cpy.short_name})
        self.assertTrue(data['is_taken'])


    def test_shortname_negative(self):
        """
        Checks if the AJAX method of checking a short name is correct
        """
        data = get_ajax("/ajax/validate_short_name/", {'short_name' : "ultra_random_string"})
        self.assertTrue(not data['is_taken'])


    def test_admin_positive(self):
        """
        Checks if the AJAX method of checking an admin is correct
        """
        admin = Administrator.objects.all()[:1].get()
        data = get_ajax("/ajax/validate_admin/", {'admin' : admin.user.username})
        self.assertTrue(data['is_taken'])


    def test_admin_negative(self):
        """
        Checks if the AJAX method of checking an admin is correct
        """
        data = get_ajax("/ajax/validate_admin/", {'admin' : "ultra_random_string"})
        self.assertTrue(not data['is_taken'])

    def test_cif_positive(self):
        """
        Checks if the AJAX method of checking an admin is correct
        """
        cpy = Company.objects.all()[:1].get()
        data = get_ajax("/ajax/validate_cif/", {'cif' : cpy.cif})
        self.assertTrue(data['is_taken'])


    def test_cif_negative(self):
        """
        Checks if the AJAX method of checking an admin is correct
        """
        data = get_ajax("/ajax/validate_cif/", {'cif' : "ultra_random_string"})
        self.assertTrue(not data['is_taken'])

    def test_view_company_positive(self):
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/company/view/")
        self.assertEquals(response.status_code, 200)

    def test_view_company_anonymous(self):
        c = Client()
        response = c.get("/company/view/")
        self.assertEquals(response.status_code, 302)
