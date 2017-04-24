from django.db import models


class CompanyLog(models.Model):
    """ Esto es una clase del modelo. Totalmente inesperado"""

    cif = models.CharField(max_length=9, unique=True)
    company_name = models.CharField(max_length=100)
    registryDate = models.DateTimeField()
    endDate = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.cif + "-" + self.company_name
