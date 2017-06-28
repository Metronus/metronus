from metronus_app.model.company         import Company
from metronus_app.model.administrator   import Administrator
from django.contrib.auth.models         import User
from django.test                        import TestCase, Client
from metronus_app.common_utils          import get_ajax
from django.urls import reverse
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
        Register new company
        """
        c = Client()

        logs_before = Company.objects.all().count()

        response = c.post(reverse("register"), {
            # Company
            "cif" :"A01234567",
            "company_name" :"comapniadejuego",
            "short_name" :"cdj",
            "company_email" :"emaildeemp@es.es",
            "company_phone":"123456987",
          

            # User (Account data)
            "username" : "usuarionumero1",
            "admin_email" : "es@es.es",
            "password" : "alcontraeslarga",
            "repeatPassword" : "alcontraeslarga",
            "first_name" :"pepito",
            "last_name" : "name1",

            # Administrator (Profile data)
            "admin_identifier" :"ide",
            "admin_phone" : "123456789",
            "terms_agree" : "True",

        })
    
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard_view"), fetch_redirect_response=False)
        # Check that the department has been successfully created

       
        logs_after = Company.objects.all().count()

        self.assertEquals(logs_before + 1, logs_after)
    def test_edit_company(self):
        """
        Edit  company
        """
        c = Client()
        c.login(username="admin1", password="123456")
        logs_before = Company.objects.all().count()

        response = c.post(reverse("company_edit"), {
            # Company
            'visible_short_name':True,
            'company_email': "compania@pes.es",
            'company_phone': "932833777",
        })
    
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse("company_view"), fetch_redirect_response=False)
        # Check that the department has been successfully created
        self.assertEquals(Company.objects.get(cif="231231F").phone,"932833777")
        self.assertEquals(Company.objects.get(cif="231231F").email,"compania@pes.es")
        logs_after = Company.objects.all().count()


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
        data = get_ajax("/ajax/validate_username/", {'username' : admin.user.username})
        self.assertTrue(data['is_taken'])


    def test_admin_negative(self):
        """
        Checks if the AJAX method of checking an admin is correct
        """
        data = get_ajax("/ajax/validate_username/", {'username' : "ultra_random_string"})
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
        """
        View company
        """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get("/company/view/")
        self.assertEquals(response.status_code, 200)

    def test_view_company_anonymous(self):
        """
        Try accessing company
        """
        c = Client()
        response = c.get("/company/view/")
        self.assertEquals(response.status_code, 302)
