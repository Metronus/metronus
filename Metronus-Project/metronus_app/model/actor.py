from django.db import models
from django.contrib.auth.models import User
from metronus_app.model.company import Company


class Actor(models.Model):

    type_choices = (('A', 'Administrator'), ('E', 'Employee'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=1, choices=type_choices, default='E')

    identifier = models.CharField(max_length=15)
    phone = models.CharField(max_length=15)

    company_id = models.ForeignKey(Company)
    registryDate = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.identifier
