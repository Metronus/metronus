from django.db import models

class Role(models.Model):
    name=models.CharField(max_length=30)
    def __unicode__(self):
        return self.name
