from django.db import models

from metronus_app.model.company import Company
from metronus_app.model.department import Department
from metronus_app.model.project import Project

class ProjectDepartment(models.Model):
    department_id = models.ForeignKey(Department)
    project_id 	= models.ForeignKey(Project)

    def __unicode__(self):
        return self.department_id.name +" - "+ self.project_id.name
