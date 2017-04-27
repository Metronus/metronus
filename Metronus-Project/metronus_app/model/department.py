from django.db import models
from metronus_app.model.company import Company


class Department(models.Model):
    """ Esto es una clase del modelo. Totalmente inesperado"""

    company_id = models.ForeignKey(Company)
    name = models.CharField(max_length=50)
    registryDate = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'company_id')
