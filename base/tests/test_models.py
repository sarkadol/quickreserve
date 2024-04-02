from django.test import TestCase
from django.contrib.auth.models import User
from base.models import Reservation
from datetime import date

from django.test import TestCase
from base.models import User, Reservation, Category, Offer, Pricing, ReservationSlot, Unit
from django.utils import timezone
from datetime import timedelta

class ReservationModelTest(TestCase):
    def setUp(self):
        # Create instances of Offer and Pricing
        offer = Offer.objects.create(offer_name="Special Offer")
        pricing = Pricing.objects.create(pricing_name="Standard", price=100)

        # Create a Category instance
        category = Category.objects.create(
            category_name="Deluxe Room",
            category_description="A luxurious room with ocean view",
            category_capacity=2,
            max_simultneous_reservations=1,
            count_of_units=10,
            created_at=timezone.now(),
            opening_time=timezone.now().time(),
            closing_time=(timezone.now() + timedelta(hours=23, minutes=59, seconds=59)).time(),
            belongs_to_offer=offer,
            category_pricing=pricing
        )

        # Assuming there's a 'Unit' model that is also related
        unit = Unit.objects.create(unit_name="A1", belongs_to_category=category)

        # Setup ReservationSlot if needed for completeness, assuming it's related to the process
        reservation_slot = ReservationSlot.objects.create(
            unit=unit,
            start_time=timezone.now(),
            duration=timedelta(hours=2),
            status="available"
        )

        # Customer details
        self.customer_email = 'customer@example.com'
        self.customer_name = 'John Doe'
        self.verification_token = 'someuniqueverificationtoken12345'

        # Reservation details
        self.reservation_from = timezone.now()
        self.reservation_to = self.reservation_from + timedelta(days=1)

    def test_reservation_creation(self):
        # Fetch the Category instance
        category = Category.objects.first()
        
        # Create a Reservation instance
        reservation = Reservation.objects.create(
            reservation_from=self.reservation_from,
            reservation_to=self.reservation_to,
            submission_time=timezone.now(),
            confirmed_by_manager="N",
            customer_email=self.customer_email,
            customer_name=self.customer_name,
            verification_token=self.verification_token,
            belongs_to_category=category,
            status='pending',
        )

        # Assertions
        self.assertTrue(isinstance(reservation, Reservation))
        self.assertEqual(reservation.customer_email, self.customer_email)
        self.assertEqual(reservation.status, 'pending')
        self.assertEqual(reservation.belongs_to_category, category)
        self.assertEqual(reservation.verification_token, self.verification_token)

        # Testing the string representation
        expected_string_representation = f"Reservation for {reservation.belongs_to_category} from {reservation.reservation_from} to {reservation.reservation_to}"
        self.assertEqual(str(reservation), expected_string_representation)
