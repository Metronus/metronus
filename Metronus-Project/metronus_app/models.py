from django.db import models

# Create your models here.
class Department(models.Model):
	companyId 	= models.ForeignKey(Company)
	name 		= models.CharField(max_length=30)
	registryDate	= models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.name
	