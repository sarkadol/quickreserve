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
from base.factories import CategoryFactory, UnitFactory, ReservationFactory, ReservationSlotFactory
from base.models import Category, Unit, Reservation, ReservationSlot
from base.optimization import optimize_category
from datetime import datetime, timedelta, time
from django.utils import timezone

class OptimizationTests(TestCase):
    def setUp(self):
        """Set up the necessary objects for the optimization tests."""
        self.category = CategoryFactory()
        self.units = UnitFactory.create_batch(5, belongs_to_category=self.category)
        self.day = timezone.now().date()

        # Create slots for each unit using the actual application logic
        opening_time =time(0, 0) # Example opening time
        closing_time = time(23, 59, 59)
        for unit in self.units:
            create_slots_for_unit(unit, self.day, opening_time, closing_time)
            print("Slot created")
        # Correcting reservation times
        self.reservations = [
            ReservationFactory(
                belongs_to_category=self.category,
                reservation_from=timezone.make_aware(datetime.combine(self.day, time(10, 0))),
                reservation_to=timezone.make_aware(datetime.combine(self.day, time(12, 0)))
            ),
            ReservationFactory(
                belongs_to_category=self.category,
                reservation_from=timezone.make_aware(datetime.combine(self.day, time(13, 0))),
                reservation_to=timezone.make_aware(datetime.combine(self.day, time(17, 0)))
            ),
            ReservationFactory(
                belongs_to_category=self.category,
                reservation_from=timezone.make_aware(datetime.combine(self.day, time(16, 0))),
                reservation_to=timezone.make_aware(datetime.combine(self.day, time(18, 0)))
            )
        ]    


    def test_optimize_category_min_units(self):
        """Test the min_units optimization strategy."""
        optimize_category(self.category, 'min_units', self.day)

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

        print("Optimization test for min_units strategy passed.")