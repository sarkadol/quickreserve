# Standard library imports
from datetime import datetime, timedelta
import datetime

# Django model imports
from django.db import models
from django.contrib.auth.models import User

# Django utilities
from django.utils import timezone

"""class Assigned(models.Model):
    #category_id = models.IntegerField(primary_key=True)
    #pricing_id = models.IntegerField(primary_key=True)
    pricing = models.ForeignKey('Pricing', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)"""
# probably do not need this, as the pricing is like ForeignKey in Category

class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='managerprofile')
    optimization_strategy = models.CharField(max_length=30, default='min_units', choices=[
        ('min_units', 'Minimal units usage'),
        ('equally_distributed', 'Equally distributed reservations')
    ])
    manager_link = models.URLField(max_length=200, blank=True)


    def __str__(self):
        return self.user.username

class Offer(models.Model):
    # offer_id = models.IntegerField(primary_key=True)
    offer_name = models.CharField(max_length=50)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    # last_edited_at
    manager_of_this_offer = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.offer_name  # rewrites Offer object (x) to its name in admi panel
    
    class Meta:
        unique_together = (
            "offer_name",
            "manager_of_this_offer",
        )  # there cannot be two same named offers managed by the same user

class Pricing(models.Model):
    # pricing_id = models.IntegerField(primary_key=True)
    pricing_name = models.CharField(max_length=50)
    price = models.IntegerField()
    pricing_time_from = models.DateField(null=True, blank=True)
    pricing_time_to = models.DateField(null=True, blank=True)
    # maybe some price value needed (12/hour, 23/room, /parkplace)
    pricing_notes = models.CharField(max_length=200, null=True, blank=True)


class Category(models.Model):
    # category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=50)
    category_description = models.CharField(max_length=1000, null=True, blank=True)
    category_capacity = models.IntegerField(default=1,help_text="How many reservations at one time are possible? e.g.seminar = 20 or parkplace = 1")
    max_simultaneous_reservations = models.IntegerField(default=1)
    additional_time = models.DurationField(null=True, blank=True,default=0) 
    # blank=True, the field is allowed to be empty in forms
    # null=True on a field allows the database to store a NULL value for that field
    count_of_units = models.IntegerField(default=1,help_text="How many units are there in this category? e.g. 5 parkplaces for disabled people")
    created_at = models.DateTimeField(default=timezone.now)
    unit_names = models.JSONField(default=list) # list of unit names
    # last_edited_at
    opening_time = models.TimeField(default=datetime.time(0, 0))
    closing_time = models.TimeField(default=datetime.time(23, 59,59)) #TODO 24:00 and default values 9:23-9:23

    belongs_to_offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    category_pricing = models.ForeignKey(Pricing, on_delete=models.CASCADE, null=True)

    # offer_user = models.ForeignKey(User, on_delete=models.CASCADE)
    def get_unit_count(self):
        return self.unit_set.count()

    def __str__(self):
        return (
            self.category_name
        )  # rewrites Category object (x) to its name in admin panel


class Unit(models.Model):
    unit_name = models.CharField(max_length=10)  # for example room A23

    belongs_to_category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )  # belongs to 4people rooms

    """class Meta:
        unique_together = (
            "unit_name",
            "belongs_to_category",
        )  # two units can have same name if they are in different category"""

    def __str__(self):
        return self.unit_name  # rewrites Category object (x) to its name in admin panel




class Reservation(models.Model):
    reservation_from = models.DateTimeField(help_text="Start time/date of the reservation")
    reservation_to = models.DateTimeField(null=True, blank=True, help_text="End time/date of the reservation")
    submission_time = models.DateTimeField(default=timezone.now, help_text="When the reservation was submitted")
    confirmed_by_manager = models.CharField(
        max_length=1,
        choices=[("A", "Confirmed"), ("N", "Not Confirmed")],
        null=True,
        blank=True,
        help_text="Whether the reservation is confirmed by a manager"
    )
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    verification_token = models.CharField(max_length=64)  # Assuming you're using a hex token

    belongs_to_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='reservations', help_text="The category of the unit being reserved")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("completed", "Completed"),
        ],
        default="pending",
        help_text="The current status of the reservation"
    )

    def __str__(self):
        return f"Reservation for {self.belongs_to_category} from {self.reservation_from} to {self.reservation_to}"

    class Meta:
        ordering = ['-submission_time'] # Reservations ordered in ascending order (earliest first)

class ReservationSlot(models.Model):
    unit = models.ForeignKey(
        Unit, related_name="reservation_slots", on_delete=models.CASCADE
    )
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name="slots")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(default=timedelta(minutes=60))

    # Consider including a status field as suggested previously
    status = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("pending", "Pending"),
            ("reserved", "Reserved"),
            ("maintenance", "Maintenance"),
            ("closed", "Closed"),

        ],
    )

    class Meta:
        unique_together = (
            "unit",
            "start_time",
        )  # two reservation slots cannost start at the same time in the same unit

    def save(self, *args, **kwargs):
        # Automatically calculate end_time before saving
        if not self.end_time:
            self.end_time = self.start_time + self.duration
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Slot in {self.unit} from {self.start_time} to {self.end_time}"