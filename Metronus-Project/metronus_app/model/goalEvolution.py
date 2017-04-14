from django.db import models
from django.contrib.auth.models import User
from metronus_app.model.actor import Actor
from metronus_app.model.task import Task
from metronus_app.model.projectDepartment import ProjectDepartment
class GoalEvolution(models.Model):
    task_id  = models.ForeignKey(Task)

    registryDate = models.DateTimeField(auto_now=True)

    actor_id = models.ForeignKey(Actor)

    production_goal=models.FloatField(blank=True,null=True)
    goal_description=models.CharField(blank=True,max_length=100,default="")

    price_per_unit=models.FloatField(null=True,blank=True)
    price_per_hour=models.FloatField(null=True,blank=True)

    def __unicode__(self):
        return self.production_goal
