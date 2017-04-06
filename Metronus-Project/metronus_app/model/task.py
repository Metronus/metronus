from django.db import models
from django.contrib.auth.models import User
from metronus_app.model.actor import Actor
from metronus_app.model.projectDepartment import ProjectDepartment
class Task(models.Model):
    name  = models.CharField(max_length=30)
    description  = models.CharField(max_length=200)
    registryDate = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    actor_id = models.ForeignKey(Actor)
    projectDepartment_id = models.ForeignKey(ProjectDepartment)

    production_goal=models.FloatField(null=True,blank=True)
    goal_description=models.CharField(blank=True,max_length=100,default="")

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('projectDepartment_id', 'name')
