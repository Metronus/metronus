from django.db import models

class Role(models.Model):
	"""
	A role, depending on the tier you can or not access some parts of Metronus
	"""
    name = models.CharField(max_length=30, unique=True)
    tier = models.PositiveSmallIntegerField(blank=False, null=False,default=10)

    def __unicode__(self):
        return self.name
