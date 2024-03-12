from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

"""class Assigned(models.Model):
    #category_id = models.IntegerField(primary_key=True)
    #pricing_id = models.IntegerField(primary_key=True)
    pricing = models.ForeignKey('Pricing', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)"""
# probably do not need this, as the pricing is like ForeignKey in Category


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_role = models.CharField(
        max_length=8,
        choices=[("CUSTOMER", "Customer"), ("MANAGER", "Manager"), ("USER", "User")],
        default="USER",
    )
    # is needed? maybe is_staff is enough


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
    category_capacity = models.IntegerField(default=1)
    max_simultneous_reservations = models.IntegerField(default=1)
    additional_time = models.DurationField(null=True, blank=True)
    max_count_of_units = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    # last_edited_at

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

    class Meta:
        unique_together = (
            "unit_name",
            "belongs_to_category",
        )  # two units can have same name if they are in different category

    def __str__(self):
        return self.unit_name  # rewrites Category object (x) to its name in admin panel


class ReservationSlot(models.Model):
    unit = models.ForeignKey(
        Unit, related_name="reservation_slots", on_delete=models.CASCADE
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # Consider including a status field as suggested previously
    status = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("maintenance", "Maintenance"),
        ],
    )


class Reservation(models.Model):
    reservation_from = models.DateTimeField()
    reservation_to = models.DateTimeField(null=True, blank=True)
    # time_of_reservation = models.DateField() #when was the reservation created

    # slot = models.ForeignKey(ReservationSlot, related_name='reservations', on_delete=models.CASCADE)

    submission_time = models.DateTimeField(
        default=timezone.now
    )  # THIS NEED DEFAULT VALUE!
    confirmed_by_manager = models.CharField(
        max_length=1,
        choices=[("A", "Confirmed"), ("N", "Not Confirmed")],
        null=True,
        blank=True,
    )

    # customer = models.ForeignKey(User, on_delete=models.CASCADE) #just for now so I can test it
    # reserved_category = models.ForeignKey(Category, on_delete=models.CASCADE) #just for now so I can test it
