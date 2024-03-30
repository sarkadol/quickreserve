from django.test import TestCase
from django.contrib.auth.models import User
from models import Reservation
from datetime import date

class ReservationModelTest(TestCase):
    def setUp(self):
        # Set up data for the whole TestCase
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_reservation_creation(self):
        # Create a Reservation instance
        reservation = Reservation.objects.create(
            reservation_date=date.today(),
            user=self.user,
            status='pending',
        )
        
        # Check that the Reservation instance has been correctly created
        self.assertTrue(isinstance(reservation, Reservation))
        self.assertEqual(reservation.user.username, 'testuser')
        self.assertEqual(reservation.status, 'pending')

        # Optionally, check the date is today
        self.assertEqual(reservation.reservation_date, date.today())
