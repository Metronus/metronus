from django.db import models
from metronus_app.model.employee import Employee


class EmployeeLog(models.Model):
    """ Esto es una clase del modelo. Totalmente inesperado"""

    employee_id = models.ForeignKey(Employee)
    event = models.CharField(max_length=1, choices=[('A', 'Alta'), ('B', 'Baja'), ('C', 'Change')], default='A')
    event_date = models.DateTimeField(auto_now=True)
    price_per_hour = models.FloatField(default=1.0)

    def __unicode__(self):
        return "{0} - {1} - {2}".format(self.employee_id , self.event , self.event_date)
