from django.db import models
from metronus_app.model.task import Task
from metronus_app.model.employee import Employee

class TimeLog(models.Model):
    """
    When an employee works on a task, he may specify how many hours has he/she spent and how many units have he/she produced.
    Essential for productivity and profit analytics to be calculated
    """
    description = models.CharField(max_length=200, blank=False, null=False)
    registryDate = models.DateTimeField(auto_now=True)
    workDate = models.DateTimeField()

	#duration in minutes
    duration = models.PositiveSmallIntegerField(default=1, blank=False, null=False)

    #produced units in task_id__goal_description units
    produced_units = models.FloatField(null=True, blank=True)

    task_id = models.ForeignKey(Task)
    employee_id = models.ForeignKey(Employee)

    def __unicode__(self):
        return self.task_id + " - " + self.workDate + " - " + self.description
