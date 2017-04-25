from django.test import Client
from django.test import TestCase


class IndexTestCase(TestCase):
    """This class provides a test case for the index. WOW!!!"""
    def test_login_employee(self):
	    c = Client()
	    response = c.get("/")
	    self.assertEquals(response.status_code, 200)
