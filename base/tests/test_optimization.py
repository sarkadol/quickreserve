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
from base.factories import (
    CategoryFactory,
    UnitFactory,
    ReservationFactory,
    ReservationSlotFactory,
    UserFactory,
    ManagerProfileFactory,
)
from base.models import (
    Category,
    Unit,
    Reservation,
    ReservationSlot,
    User,
    ManagerProfile,
    Offer,
)
from base.optimization import optimize_category
from datetime import datetime, timedelta, time
from django.utils import timezone
import time as time_module

number_of_reservations = 6
number_of_units = 16
optimization_strategy = "equally_distributed"
#optimization_strategy = "min_units"


class OptimizationTests(TestCase):
    def setUp(self):
        """Set up the necessary objects for the optimization tests."""
        # Create a manager user and profile using factories
        self.manager_user = UserFactory(username="manager")
        self.manager_profile = ManagerProfileFactory(
            user=self.manager_user, optimization_strategy=optimization_strategy
        )

        # Create an Offer linked to this manager
        self.offer = OfferFactory(manager_of_this_offer=self.manager_user)

        # Create a Category that belongs to this Offer using CategoryFactory
        self.category = CategoryFactory(belongs_to_offer=self.offer)
        self.units = UnitFactory.create_batch(
            number_of_units, belongs_to_category=self.category
        )
        self.day = timezone.now().date()

        # Create slots for each unit using the actual application logic
        opening_time = time(8, 0)  # Example opening time
        closing_time = time(23, 59, 59)
        for unit in self.units:
            create_slots_for_unit(unit, self.day, opening_time, closing_time)

        # Correcting reservation times

        # Create 100 reservations with random start times and durations
        self.reservations = []
        for _ in range(number_of_reservations):
            start_hour = randint(
                0, 22
            )  # Reserve up to the 22nd hour to allow at least 1 hour duration
            duration_hours = randint(1, 2)  # Duration between 1 and 2 hours
            reservation_start = timezone.make_aware(
                datetime.combine(self.day, time(start_hour, 0))
            )
            reservation_end = reservation_start + timedelta(hours=duration_hours)
            reservation = ReservationFactory(
                belongs_to_category=self.category,
                reservation_from=reservation_start,
                reservation_to=reservation_end,
            )
            self.reservations.append(reservation)

    def test_optimize_category_min_units(self):
        """Test the min_units optimization strategy."""

        start_time = time_module.time()  # Start timing using the time module
        optimize_category(self.category, self.day)
        end_time = time_module.time()  # Start timing using the time module

        # Retrieve all slots post-optimization to check assignments
        all_slots = ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        )

        # Check that reservations are not overlapping within units
        for unit in self.units:
            unit_slots = all_slots.filter(unit=unit).order_by("start_time")
            last_end_time = None
            for slot in unit_slots:
                if slot.reservation:
                    if last_end_time and slot.start_time < last_end_time:
                        self.fail(f"Overlapping reservation found in unit {unit.id}")
                    last_end_time = slot.end_time

        # Optionally, check the minimum number of units used
        used_units = {slot.unit.id for slot in all_slots if slot.reservation}
        print(f"Used units: {used_units}")
        self.assertTrue(
            len(used_units) <= len(self.reservations), "More units used than necessary"
        )
        print("Duration: ", end_time - start_time, " seconds")

        print("Optimization test for min_units strategy passed.")

    def test_optimize_category_min_units_consistency(self):
        """Test the min_units optimization strategy consistency over multiple runs."""
        print("CONSISTENCY TEST")
        # First optimization run
        optimize_category(self.category, self.day)
        first_run_slots = ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        ).values_list("unit_id", "reservation_id")

        # Clear slots for second run
        ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        ).update(reservation=None)

        # Second optimization run
        optimize_category(self.category, self.day)
        second_run_slots = ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        ).values_list("unit_id", "reservation_id")

        # Compare the results of the two runs
        self.assertEqual(
            set(first_run_slots),
            set(second_run_slots),
            "The optimization results differ between runs.",
        )

    def test_optimization_stability_with_additional_non_overlapping_reservation(self):
        """Test that the optimization does not unnecessarily change existing reservation assignments with the addition of a non-overlapping reservation."""
        # Initial optimization run
        print("STABILITY WITHOUT OVERLAP")
        optimize_category(self.category, self.day)
        initial_assignments = {
            slot.id: slot.reservation.id
            for slot in ReservationSlot.objects.filter(
                unit__belongs_to_category=self.category, start_time__date=self.day
            )
            if slot.reservation
        }

        # Determine non-overlapping time for the additional reservation
        all_slots = ReservationSlot.objects.filter(
            unit__belongs_to_category=self.category, start_time__date=self.day
        )
        occupied_slots = set(slot.start_time for slot in all_slots if slot.reservation)
        slot_duration = timedelta(
            hours=1
        )  # assuming slot duration is 1 hour for simplicity
        available_slots = [
            datetime.combine(self.day, time(hour))
            for hour in range(24)
            if timezone.make_aware(datetime.combine(self.day, time(hour)))
            not in occupied_slots
        ]

        if not available_slots:
            self.skipTest("No available slots to test non-overlapping reservation.")

        # Add an additional reservation
        additional_reservation_start = available_slots[
            0
        ]  # pick the first available slot
        additional_reservation_end = additional_reservation_start + slot_duration
        ReservationFactory(
            belongs_to_category=self.category,
            reservation_from=additional_reservation_start,
            reservation_to=additional_reservation_end,
        )

        # Second optimization run after adding the reservation
        optimize_category(self.category, self.day)
        post_addition_assignments = {
            slot.id: slot.reservation.id
            for slot in ReservationSlot.objects.filter(
                unit__belongs_to_category=self.category, start_time__date=self.day
            )
            if slot.reservation
        }

        # Check that original reservations maintain their slots if no new assignment is necessary
        unchanged = True
        for slot_id, reservation_id in initial_assignments.items():
            if (
                slot_id in post_addition_assignments
                and post_addition_assignments[slot_id] != reservation_id
            ):
                unchanged = False
                break

        self.assertTrue(
            unchanged, "Original reservation assignments changed unnecessarily."
        )
        print(
            "Optimization maintains stability with additional non-overlapping reservation."
        )
