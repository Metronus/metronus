from django.db import models

class Company(models.Model):
    cif=models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    logo=models.BinaryField()
    email= models.EmailField()
    phone= models.CharField(max_length=15)
    pswd= models.CharField(max_length=255)
    registryDate = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name
