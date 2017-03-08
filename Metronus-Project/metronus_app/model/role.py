from django.db import models
from metronus_app.model.company import Company

class Role(models.Model):

    name = models.CharField(max_length=50)
    company_id = models.ForeignKey(Company)

    def __unicode__(self):
        return self.name
