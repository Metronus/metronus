from metronus_app.model.administrator import Administrator
from django.contrib.auth.models import User
from django.test import TestCase, Client
from metronus_app.model.company import Company
import json

class AdministratorTestCase(TestCase):
    """This class provides a test case for administrator management"""
    def setUp(self):
        """
        Loads the data to the database for tests to be done
        """
        company1 = Company.objects.create(
            cif="123",
            company_name="company1",
            short_name="mplp",
            email="company1@gmail.com",
            phone="123456789"
        )

        company2 = Company.objects.create(
            cif="456",
            company_name="company2",
            short_name="lmao",
            email="company2@gmail.com",
            phone="1987654321"
        )

        admin_user = User.objects.create_user(
            username="admin1",
            password="123456",
            email="admin1@metronus.es",
            first_name="Pepito",
            last_name="Pérez"
        )

        # Admin
        Administrator.objects.create(
            user=admin_user,
            user_type="A",
            identifier="adm01",
            phone="666555444",
            company_id=company1
        )

    def test_edit_admin_get(self):
        """
        As an admin, get the edit admin form
        """
        c = Client()
        c.login(username="admin1", password="123456")

        response = c.get("/administrator/edit/")
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]

        self.assertEquals(form.initial["first_name"], "Pepito")
        self.assertEquals(form.initial["last_name"], "Pérez")
        self.assertEquals(form.initial["admin_email"], "admin1@metronus.es")
        self.assertEquals(form.initial["identifier"], "adm01")
        self.assertEquals(form.initial["phone"], "666555444")

    def test_edit_admin_negative_invalid_form(self):
        """
        As an admin, edit its profile
        """
        c = Client()
        c.login(username="admin1", password="123456")

        
        response = c.post("/administrator/edit/", {
            "first_name": "NuevoNombre",
            "last_name": "NuevoApellido",
            "admin_email": "nuevocorreo@empresa.com",
            "identifier": "",
            "phone": "nuevotelefono",
            "price_per_hour": "",
        })
        self.assertEquals(response.status_code, 200)


    def test_edit_admin_positive_without_pass(self):
        """
        As an admin, edit its profile without pass
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="admin1").password
        
        response = c.post("/administrator/edit/", {
            "first_name": "NuevoNombre",
            "last_name": "NuevoApellido",
            "admin_email": "nuevocorreo@empresa.com",
            "identifier": "nuevoid",
            "phone": "456456456",
        })

        self.assertRedirects(response, "/company/view/", fetch_redirect_response=False)

        final = Administrator.objects.get(user__username="admin1")
        self.assertEquals(final.identifier, "nuevoid")
        self.assertEquals(final.phone, "456456456")
        self.assertEquals(final.user.first_name, "NuevoNombre")
        self.assertEquals(final.user.last_name, "NuevoApellido")
        self.assertEquals(final.user.email, "nuevocorreo@empresa.com")
        self.assertEquals(final.user.password, initialpass)


    def test_edit_admin_pass_positive(self):
        """
        As an admin, edit an admin password
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="admin1").password

        c.post("/administrator/updatePassword", {
            "newpass1": "nuevapassword",
            "newpass2": "nuevapassword",
            "currentpass": "123456",
        })

        final = Administrator.objects.get(user__username="admin1")
        self.assertTrue(final.user.password != initialpass)

    def test_edit_admin_pass_negative(self):
        """
        As an admin, try editing its password when password repeat do not match
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="admin1").password

        response =c.post("/administrator/updatePassword", {
            "newpass1": "nuevapassword",
            "newpass2": "ojala morir",
            "currentpass": "123456",
        })

        final = Administrator.objects.get(user__username="admin1")
        self.assertTrue(final.user.password == initialpass)
        
        #response in bytes must be decode to string
        data=response.content.decode("utf-8")
        #string to dict
        data=json.loads(data)
        self.assertEquals(data["success"],False)
        self.assertTrue('passwordsDontMatch' in data["errors"])

    def test_edit_admin_pass_negative_2(self):
        """
        As an admin, wrong new password
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="admin1").password

        response =c.post("/administrator/updatePassword", {
            "newpass1": "122",
            "newpass2": "122",
            "currentpass": "123456",
        })

        final = Administrator.objects.get(user__username="admin1")
        self.assertTrue(final.user.password == initialpass)
        
        #response in bytes must be decode to string
        data=response.content.decode("utf-8")
        #string to dict
        data=json.loads(data)
        self.assertEquals(data["success"],False)
        self.assertTrue('newPasswordInvalid' in data["errors"])

    def test_edit_admin_pass_negative_3(self):
        """
        As an admin, wrong current password
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="admin1").password

        response =c.post("/administrator/updatePassword", {
            "newpass1": "nuevapassword",
            "newpass2": "nuevapassword",
            "currentpass": "12356",
        })

        final = Administrator.objects.get(user__username="admin1")
        self.assertTrue(final.user.password == initialpass)
        
        #response in bytes must be decode to string
        data=response.content.decode("utf-8")
        #string to dict
        data=json.loads(data)
        self.assertEquals(data["success"],False)
        self.assertTrue('currentPasswordInvalid' in data["errors"])

    def test_edit_admin_pass_negative_4(self):
        """
        As an admin, wrong form
        """
        c = Client()
        c.login(username="admin1", password="123456")

        initialpass = User.objects.get(username="admin1").password

        response =c.post("/administrator/updatePassword", {
            "newpass1": "nuevapassword",
            "currentpass": "123456",
        })

        final = Administrator.objects.get(user__username="admin1")
        self.assertTrue(final.user.password == initialpass)
        
        #response in bytes must be decode to string
        data=response.content.decode("utf-8")
        #string to dict
        data=json.loads(data)
        self.assertEquals(data["success"],False)
        self.assertTrue('formNotValid' in data["errors"])

    def test_edit_admin_not_allowed_password(self):
        """
        Try editing an admin password without login
        """
        c = Client()
      
        response = c.get("/administrator/updatePassword")
        self.assertEquals(response.status_code, 403)

    def test_edit_admin_not_allowed(self):
        """
        Try editing an admin without login
        """
        c = Client()
      
        response = c.get("/administrator/edit/")
        self.assertEquals(response.status_code, 302)



