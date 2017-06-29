from metronus_app.model.company         import Company
from metronus_app.model.administrator   import Administrator
from django.contrib.auth.models         import User
from django.test                        import TestCase, Client
from metronus_app.common_utils          import get_ajax
from django.urls import reverse
import json


class CompanyTestCase(TestCase):
    """This class provides a test case for companies signing up to the system"""
    @classmethod
    def setUpTestData(cls):
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
        company2 = Company.objects.create(
            cif="231232F",
            company_name="Universidad de Sevilla2",
            short_name="us2",
            email="us2@gmail.com",
            phone="123456789")

        admin_user2 = User.objects.create_user(
            username="admin2",
            password="123456",
            email="admin2@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        Administrator.objects.create(
            user=admin_user2,
            user_type="A",
            identifier="adm023",
            phone="666555444",
            company_id=company2
        )
    def test_register_company_get(self):
        """Register new company form """
        c = Client()
        response = c.get(reverse("register"))
    
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertFalse(form is None)

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
    
    def test_create_company_negative_1(self):
        """
        Register new company, agree_terms_error
        """
        c = Client()

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
            "terms_agree" : "False",

        })
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('agree_terms_error' in response.context["errors"])   
    def test_create_company_negative_2(self):
        """
        Register new company, company_short_name_duplicate
        """
        c = Client()

        response = c.post(reverse("register"), {
            # Company
            "cif" :"A01234567",
            "company_name" :"comapniadejuego",
            "short_name" :"us",
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
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('company_short_name_duplicate' in response.context["errors"])   
    def test_create_company_negative_3(self):
        """
        Register new company, companyRegister_cifNotUnique
        """
        c = Client()

        response = c.post(reverse("register"), {
            # Company
            "cif" :"231231F",
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
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('companyRegister_cifNotUnique' in response.context["errors"])   
    def test_create_company_negative_4(self):
        """
        Register new company, companyRegister_adminEmailNotUnique
        """
        c = Client()

        response = c.post(reverse("register"), {
            # Company
            "cif" :"A01234567",
            "company_name" :"comapniadejuego",
            "short_name" :"cdj",
            "company_email" :"emaildeemp@es.es",
            "company_phone":"123456987",
          

            # User (Account data)
            "username" : "usuarionumero1",
            "admin_email" : "admin1@metronus.es",
            "password" : "alcontraeslarga",
            "repeatPassword" : "alcontraeslarga",
            "first_name" :"pepito",
            "last_name" : "name1",

            # Administrator (Profile data)
            "admin_identifier" :"ide",
            "admin_phone" : "123456789",
            "terms_agree" : "True",

        })
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('companyRegister_adminEmailNotUnique' in response.context["errors"])   
    
    def test_create_company_negative_5(self):
        """
        Register new company, companyRegister_companyEmailNotUnique
        """
        c = Client()

        response = c.post(reverse("register"), {
            # Company
            "cif" :"A01234567",
            "company_name" :"comapniadejuego",
            "short_name" :"cdj",
            "company_email" :"us@gmail.com",
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
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('companyRegister_companyEmailNotUnique' in response.context["errors"])   
    

    def test_create_company_negative_6(self):
        """
        Register new company, newPasswordInvalid
        """
        c = Client()

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
            "password" : "alcoa",
            "repeatPassword" : "alcoa",
            "first_name" :"pepito",
            "last_name" : "name1",

            # Administrator (Profile data)
            "admin_identifier" :"ide",
            "admin_phone" : "123456789",
            "terms_agree" : "True",

        })
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('newPasswordInvalid' in response.context["errors"])   
    def test_create_company_negative_7(self):
        """
        Register new company, companyRegister_usernameNotUnique
        """
        c = Client()

        response = c.post(reverse("register"), {
            # Company
            "cif" :"A01234567",
            "company_name" :"comapniadejuego",
            "short_name" :"cdj",
            "company_email" :"emaildeemp@es.es",
            "company_phone":"123456987",
          

            # User (Account data)
            "username" : "admin1",
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
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('companyRegister_usernameNotUnique' in response.context["errors"])   
    def test_create_company_negative_8(self):
        """
        Register new company, passwordsDontMatch
        """
        c = Client()

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
            "repeatPassword" : "alcontraeslargae",
            "first_name" :"pepito",
            "last_name" : "name1",

            # Administrator (Profile data)
            "admin_identifier" :"ide",
            "admin_phone" : "123456789",
            "terms_agree" : "True",

        })
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('passwordsDontMatch' in response.context["errors"])   
    
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
    def test_edit_company_negative(self):
        """
        Edit  company, negative email
        """
        c = Client()
        c.login(username="admin1", password="123456")
        

        response = c.post(reverse("company_edit"), {
            # Company
            'visible_short_name':True,
            'company_email': "us2@gmail.com",
            'company_phone': "932833777",
        })
    
        self.assertEquals(response.status_code, 200)
        self.assertTrue('companyRegister_companyEmailNotUnique' in response.context["errors"])   

    def test_edit_company_get(self):
        """As an admin, try to get the edit company form """
        c = Client()
        c.login(username="admin1", password="123456")
        response = c.get(reverse("company_edit"))
    
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["company_email"], "us@gmail.com")
        self.assertEquals(form.initial["company_phone"], "123456789")


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
