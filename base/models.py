from django.db import models

# Create your models here.

class Offer(models.Model):
    offer_name = models.CharField(max_length=200)
    to_date = models.DateTimeField()
    from_date = models.DateTimeField()

class Unit(models.Model):
    unit_name = models.CharField(max_length=200)
    capacity = models.IntegerField()
    offer = models.ForeignKey("Offer",on_delete=models.CASCADE)
