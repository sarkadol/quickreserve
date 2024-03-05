from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

"""class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_name = models.CharField(max_length=50)
    user_surname = models.CharField(max_length=50)
    user_email = models.CharField(max_length=50)
    user_notes = models.CharField(max_length=200, null=True, blank=True)
    user_type = models.CharField(max_length=8, choices=[('CUSTOMER', 'Customer'), ('MANAGER', 'Manager'), ('USER', 'User')])
"""
class Assigned(models.Model):
    #unit_id = models.IntegerField(primary_key=True)
    #pricing_id = models.IntegerField(primary_key=True)
    pricing = models.ForeignKey('Pricing', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_role = models.CharField(max_length=8, choices=[('CUSTOMER', 'Customer'), ('MANAGER', 'Manager'), ('USER', 'User')], default='USER')

class Offer(models.Model):
    #offer_id = models.IntegerField(primary_key=True)
    offer_name = models.CharField(max_length=50)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE,limit_choices_to={"user_role": 'Manager'}, null=True)


class Unit(models.Model):
    #unit_id = models.IntegerField(primary_key=True)
    unit_name = models.CharField(max_length=50)
    unit_description = models.CharField(max_length=1000, null=True, blank=True)
    unit_capacity = models.IntegerField()
    max_simultneous_reservations = models.IntegerField(default=1)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    additional_time = models.DateField(null=True, blank=True)
    offer_user = models.ForeignKey(User, on_delete=models.CASCADE)
    max_count_of_units = models.IntegerField()    

class Pricing(models.Model):
    #pricing_id = models.IntegerField(primary_key=True)
    pricing_name = models.CharField(max_length=50)
    price = models.IntegerField()
    pricing_time_from = models.DateField(null=True, blank=True)
    pricing_time_to = models.DateField(null=True, blank=True)
    pricing_notes = models.CharField(max_length=200, null=True, blank=True)

class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    rezervation_from = models.DateField()
    reservation_to = models.DateField()
    time_of_reservation = models.DateField()
    confirmed_by_manager = models.CharField(max_length=1, choices=[('A', 'Confirmed'), ('N', 'Not Confirmed')])

