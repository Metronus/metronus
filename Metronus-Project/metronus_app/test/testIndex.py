from django.test import Client
from django.test import TestCase
from populate_database import populate_database
from django.urls import reverse
class IndexTestCase(TestCase):
    """This class provides a test case for the index. WOW!!!"""
    
    @classmethod
    def setUpTestData(cls):
        """
        Loads the data to the database for tests to be done
        """
        populate_database()

    def test_main_page(self):
        """
        Main page
        """
        c = Client()
        response = c.get("/")
        self.assertEquals(response.status_code, 200)
    
    def test_app_page_not_logged(self):
        """
        Main app page
        """
        c = Client()
        response = c.get(reverse("app_index"))
        self.assertEquals(response.status_code, 302)

    def test_login_employee(self):
        """
        Logs in as an employee
        """
        c = Client()
        c.login(username="metronus", password="metronus")
        response = c.get("/index.html/")
        self.assertRedirects(response,"/dashboard/view" , fetch_redirect_response=False)

    def test_login_admin(self):
        """
        Logs in as an admin
        """
        c = Client()
        c.login(username="ddlsb", password="123456")
        response = c.get("/index.html/")
        self.assertRedirects(response, "/timeLog/list_all", fetch_redirect_response=False)
    def test_cookies(self):
        """
        Cookies
        """
        c = Client()
        response = c.get(reverse("cookie_policy"))
        self.assertEquals(response.status_code, 200)
    def test_legal_terms(self):
        """
        Legal terms page
        """
        c = Client()
        response = c.get(reverse("legal_terms"))
        self.assertEquals(response.status_code, 200)
