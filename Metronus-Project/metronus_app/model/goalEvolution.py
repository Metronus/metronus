from django.db import models
from metronus_app.model.actor import Actor
from metronus_app.model.task import Task


class GoalEvolution(models.Model):
    """
    Each time the goal or the price per unit/hour from a task is changed, a new entry is created in the log
    Maybe should have been named TaskLog, but...
    """
    task_id = models.ForeignKey(Task)

    registryDate = models.DateTimeField(auto_now=True)

    actor_id = models.ForeignKey(Actor)

    production_goal = models.FloatField(blank=True, null=True)
    goal_description = models.CharField(blank=True, max_length=100, default="")

    price_per_unit = models.FloatField(null=True, blank=True)
    price_per_hour = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return self.production_goal
