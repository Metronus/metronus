from django.db import models
from metronus_app.model.employee import Employee

class EmployeeLog(models.Model):
    employee_id = models.ForeignKey(Employee)
    event = models.CharField(max_length=1, choices=[('A', 'Alta'), ('B', 'Baja')], default='A')
    event_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.employee_id + "-" + self.event + "-" + self.event_date
