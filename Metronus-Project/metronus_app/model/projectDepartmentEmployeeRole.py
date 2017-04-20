from django.db import models

from metronus_app.model.role import Role
from metronus_app.model.employee import Employee
from metronus_app.model.projectDepartment import ProjectDepartment
class ProjectDepartmentEmployeeRole(models.Model):
    """
    Assigns a role to an employee
    """
    projectDepartment_id=models.ForeignKey(ProjectDepartment, on_delete=models.CASCADE);
    employee_id=models.ForeignKey(Employee);
    role_id=models.ForeignKey(Role);
    roleDate=models.DateTimeField(auto_now=True);

    class Meta:
        unique_together = ('projectDepartment_id', 'employee_id','role_id')
