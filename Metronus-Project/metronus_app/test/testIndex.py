from django.test import Client
from django.test import TestCase
from populate_database import populate_database

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

    def test_login_admin(self):
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
