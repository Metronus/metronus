from django.db import models
from metronus_app.model.company import Company

class Employee(models.Model):
    name=models.CharField(max_length=50);
    surname=models.CharField(max_length=100);
    identifier=models.CharField(max_length=15);
    registryDate= models.DateTimeField(auto_now=True)
    email=models.CharField(max_length=30);
    phone=models.CharField(max_length=15);
    pswd=models.CharField(max_length=255);
    company_id=models.ForeignKey(Company);
    def __unicode__(self):
        return self.name
