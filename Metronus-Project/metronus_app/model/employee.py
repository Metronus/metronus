from metronus_app.model.actor import Actor
from django.db import models


class Employee(Actor):
    """ Hace cosas """

    price_per_hour = models.FloatField(default=1.0)

    def __unicode__(self):
        return self.identifier
