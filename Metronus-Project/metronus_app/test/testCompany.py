from metronus_app.model.company import Company

from django.test import TestCase


class CompanyTestCase(TestCase):

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
        count2=Company.objects.count()
        self.assertTrue(count1+1, count2)

