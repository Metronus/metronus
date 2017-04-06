from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=30, unique=True)
    tier = models.PositiveSmallIntegerField(blank=False, null=False,default=10)

    def __unicode__(self):
        return self.name
