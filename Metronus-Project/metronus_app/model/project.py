from django.db import models
from metronus_app.model.company import Company


class Project(models.Model):
    """ Esto es una clase del modelo. Totalmente inesperado"""
    company_id = models.ForeignKey(Company)
    name = models.CharField(max_length=30)
    registryDate = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'company_id')
