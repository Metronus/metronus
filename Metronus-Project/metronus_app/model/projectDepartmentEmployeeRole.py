from django.db import models

from metronus_app.model.role import Role
from metronus_app.model.employee import Employee
from metronus_app.model.projectDepartment import ProjectDepartment
class ProjectDepartmentEmployeeRole(models.Model):
    projectDepartment_id=models.ForeignKey(ProjectDepartment);
    employee_id=models.ForeignKey(Employee);
    role_id=models.ForeignKey(Role);
    roleDate=models.DateTimeField();

    class Meta:
        unique_together = ('projectDepartment_id', 'employee_id','role_id')
