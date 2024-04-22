from random import randint
from django.test import TestCase
from base.factories import (
    CategoryFactory,
    OfferFactory,
    UnitFactory,
    ReservationFactory,
    ReservationSlotFactory,
)
from base.models import ReservationSlot
from base.optimization import optimize_category

from django.test import TestCase

from base.views import create_slots_for_unit





# Add similar methods for other factories to pinpoint the problematic factory.
from django.test import TestCase
from base.factories import CategoryFactory, UnitFactory, ReservationFactory, ReservationSlotFactory,UserFactory,ManagerProfileFactory
from base.models import Category, Unit, Reservation, ReservationSlot, User,ManagerProfile,Offer
from base.optimization import optimize_category
from datetime import datetime, timedelta, time
from django.utils import timezone
import time as time_module

number_of_reservations = 5
number_of_units = 5


class OptimizationTests(TestCase):
    def setUp(self):
        """Set up the necessary objects for the optimization tests."""
        # Create a manager user and profile using factories
        self.manager_user = UserFactory(username='manager')
        self.manager_profile = ManagerProfileFactory(user=self.manager_user, optimization_strategy='min_units')

        # Create an Offer linked to this manager
        self.offer = OfferFactory(manager_of_this_offer=self.manager_user)

        # Create a Category that belongs to this Offer using CategoryFactory
        self.category = CategoryFactory(belongs_to_offer=self.offer)
        self.units = UnitFactory.create_batch(number_of_units, belongs_to_category=self.category)
        self.day = timezone.now().date()

        # Create slots for each unit using the actual application logic
        opening_time =time(8, 0) # Example opening time
        closing_time = time(23, 59, 59)
        for unit in self.units:
            create_slots_for_unit(unit, self.day, opening_time, closing_time)
            
        # Correcting reservation times
            
        # Create 100 reservations with random start times and durations
        self.reservations = []
        for _ in range(number_of_reservations):
            start_hour = randint(0, 22)  # Reserve up to the 22nd hour to allow at least 1 hour duration
            duration_hours = randint(1, 2)  # Duration between 1 and 2 hours
            reservation_start = timezone.make_aware(datetime.combine(self.day, time(start_hour, 0)))
            reservation_end = reservation_start + timedelta(hours=duration_hours)
            reservation = ReservationFactory(
                belongs_to_category=self.category,
                reservation_from=reservation_start,
                reservation_to=reservation_end
            )
            self.reservations.append(reservation)


    def test_optimize_category_min_units(self):
        """Test the min_units optimization strategy."""

        start_time = time_module.time()  # Start timing using the time module
        optimize_category(self.category, self.day)
        end_time = time_module.time()  # Start timing using the time module


        # Retrieve all slots post-optimization to check assignments
        all_slots = ReservationSlot.objects.filter(unit__belongs_to_category=self.category, start_time__date=self.day)

        # Check that reservations are not overlapping within units
        for unit in self.units:
            unit_slots = all_slots.filter(unit=unit).order_by('start_time')
            last_end_time = None
            for slot in unit_slots:
                if slot.reservation:
                    if last_end_time and slot.start_time < last_end_time:
                        self.fail(f"Overlapping reservation found in unit {unit.id}")
                    last_end_time = slot.end_time

        # Optionally, check the minimum number of units used
        used_units = {slot.unit.id for slot in all_slots if slot.reservation}
        print(f"Used units: {used_units}")
        self.assertTrue(len(used_units) <= len(self.reservations), "More units used than necessary")
        print("Duration: ",end_time-start_time," seconds")

        print("Optimization test for min_units strategy passed.")

    def test_optimize_category_min_units_consistency(self):
        """Test the min_units optimization strategy consistency over multiple runs."""
        print("CONSISTENCY TEST")
        # First optimization run
        optimize_category(self.category, self.day)
        first_run_slots = ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        ).values_list('unit_id', 'reservation_id')

        # Clear slots for second run
        ReservationSlot.objects.filter(unit__belongs_to_category=self.category, start_time__date=self.day).update(reservation=None)

        # Second optimization run
        optimize_category(self.category, self.day)
        second_run_slots = ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        ).values_list('unit_id', 'reservation_id')

        # Compare the results of the two runs
        self.assertEqual(set(first_run_slots), set(second_run_slots), "The optimization results differ between runs.")    