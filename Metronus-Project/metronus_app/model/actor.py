from django.db import models
from django.contrib.auth.models import User
from metronus_app.model.company import Company

import os
from django.conf import settings
User._meta.get_field('email')._unique = True


class Actor(models.Model):
    """
    An actor who uses Metronus. Can be an adminstrator or an employee
    """
    type_choices = (('A', 'Administrator'), ('E', 'Employee'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=1, choices=type_choices, default='E')

    identifier = models.CharField(max_length=15)
    phone = models.CharField(max_length=15)

    company_id = models.ForeignKey(Company)
    registryDate = models.DateTimeField(auto_now=True)

    picture = models.ImageField(upload_to="actor", blank=True, null=True,
                                default=os.path.join(settings.STATIC_URL, 'avatar.png'))

    def __unicode__(self):
        return self.identifier

    def role(self):
        return self.type_choices(self.user_type)
