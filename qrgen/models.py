from django.db import models

# Create your models here.
class Gen(models.Model):
  data = models.CharField(max_length=100)
  number = models.IntegerField()
