from django.test import TestCase
from django.contrib.auth.models import User
from base.models import User, Reservation, Category, Offer, Pricing, ReservationSlot, Unit
from django.utils import timezone
from datetime import timedelta

class ReservationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.offer = Offer.objects.create(offer_name="Special Offer")
        cls.pricing = Pricing.objects.create(pricing_name="Standard", price=100)
        cls.category = Category.objects.create(
            category_name="Deluxe Room",
            category_description="A luxurious room with ocean view",
            category_capacity=2,
            max_simultaneous_reservations=1,
            count_of_units=10,
            created_at=timezone.now(),
            opening_time=timezone.now().time(),
            closing_time=(timezone.now() + timedelta(hours=23, minutes=59, seconds=59)).time(),
            belongs_to_offer=cls.offer,
            category_pricing=cls.pricing
        )
        cls.unit = Unit.objects.create(unit_name="A1", belongs_to_category=cls.category)
        cls.reservation_slot = ReservationSlot.objects.create(
            unit=cls.unit,
            start_time=timezone.now(),
            duration=timedelta(hours=2),
            status="available"
        )
        cls.customer_email = 'customer@example.com'
        cls.customer_name = 'John Doe'
        cls.verification_token = 'someuniqueverificationtoken12345'
        cls.reservation_from = timezone.now()
        cls.reservation_to = cls.reservation_from + timedelta(days=1)

    def test_reservation_creation(self):
        reservation = Reservation.objects.create(
            reservation_from=self.reservation_from,
            reservation_to=self.reservation_to,
            submission_time=timezone.now(),
            confirmed_by_manager="N",
            customer_email=self.customer_email,
            customer_name=self.customer_name,
            verification_token=self.verification_token,
            belongs_to_category=self.category,
            status='pending',
        )
        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.customer_email, self.customer_email)
        self.assertEqual(reservation.status, 'pending')
        self.assertEqual(reservation.belongs_to_category, self.category)
        self.assertEqual(reservation.verification_token, self.verification_token)
        expected_str = f"Reservation for {reservation.belongs_to_category} from {reservation.reservation_from} to {reservation.reservation_to}"
        self.assertEqual(str(reservation), expected_str)

    def test_category_reverse_relation(self):
        reservation = Reservation.objects.create(
            reservation_from=self.reservation_from,
            reservation_to=self.reservation_to,
            customer_email=self.customer_email,
            belongs_to_category=self.category,
            status='pending',
        )
        self.assertIn(reservation, self.category.reservation_set.all())

    def test_future_reservation_check(self):
        reservation = Reservation.objects.create(
            reservation_from=timezone.now() + timedelta(days=1),
            reservation_to=timezone.now() + timedelta(days=2),
            customer_email=self.customer_email,
            belongs_to_category=self.category,
            status='pending',
        )
        self.assertTrue(reservation.is_future_reservation())

### Additional Test Suggestions:
"""1. **Boundary Conditions**: Test the limits of category capacity.
2. **Edge Times**: Test reservations exactly at opening and closing times.
3. **Error Cases**: Ensure that creating reservations outside of permissible times or over capacity fails as expected.
4. **Concurrency**: Test that the system correctly handles simultaneous bookings that may lead to overcapacity if not managed correctly.
"""