from django.db import models

# Create your models here.
class Department(models.Model):
	company_id 	= models.ForeignKey(Company)
	name 		= models.CharField(max_length=30)
	registryDate	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.name
	
class Project(modelsModel):
	company_id 	= models.ForeignKey(Company)
	name 		= models.CharField(max_length=30)
	registryDate	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.name


class ProjectDepartment(modelsModel):
	department_id 	= models.ForeignKey(Department)
	project_id 	= models.ForeignKey(Project)
	