from django.db import models
from metronus_app.model.task import Task
from metronus_app.model.employee import Employee

class TimeLog(models.Model):
    description = models.CharField(max_length=200, blank=False, null=False)
    registryDate = models.DateTimeField(auto_now=True)
    workDate = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(default=1, blank=False, null=False)

    task_id = models.ForeignKey(Task)
    employee_id = models.ForeignKey(Employee)

    def __unicode__(self):
        return self.task_id + " - " + self.workDate + " - " + self.description