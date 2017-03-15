from django.db import models


class Company(models.Model):
    cif = models.CharField(max_length=9, unique=True)
    company_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    visible_short_name = models.BooleanField(default=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    registryDate = models.DateTimeField(auto_now=True)

    logo = models.ImageField(upload_to="company", blank=True, null=True)

    def __unicode__(self):
        return self.name
