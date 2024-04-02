from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from base.views import ensure_availability_for_day
from models import *
from datetime import date

class CategoryCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='manager', password='test123')
        self.client.login(username='manager', password='test123')
        self.offer = Offer.objects.create(offer_name="Special Offer", manager_of_this_offer=self.user)

    def test_create_category(self):
        url = reverse('create_category', args=[self.offer.id])  # Adjust based on your URL configuration
        response = self.client.post(url, {
            'category_name': 'Deluxe Rooms',
            'category_description': 'Spacious and luxurious rooms with sea view',
            'belongs_to_offer': self.offer.id,
            # Add other required fields
        })
        
        # Now expecting a redirect, ensure your view redirects on successful form submission
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(category_name='Deluxe Rooms').exists())

class ReservationSubmissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user1', 'user1@example.com', 'userpassword')
        self.category = Category.objects.create(
            category_name='Standard Room', 
            opening_time='09:00', 
            closing_time='21:00', 
            count_of_units=10)
        self.offer = Offer.objects.create(offer_name="Seasonal Offer", manager_of_this_offer=self.user)

    def test_reservation_submission(self):
        self.client.force_login(self.user)
        form_data = {
            'customer_email': 'customer@example.com',
            'reservation_date_from': datetime.now().date().strftime("%Y-%m-%d"),
            'reservation_time_from': '10:00',
            'reservation_date_to': (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d"),
            'reservation_time_to': '11:00',
            'belongs_to_category': self.category.id,
            'status': 'pending',
        }

        response = self.client.post(reverse('new_reservation', args=[self.offer.id, self.category.id]), form_data)
        self.assertEqual(response.status_code, 302)  # Assuming redirection after successful submission
        self.assertTrue(Reservation.objects.exists())

class ReservationSlotCreationTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name="Meeting Room",
            count_of_units=1
        )
        self.unit = Unit.objects.create(
            unit_name="Room 101",
            belongs_to_category=self.category
        )

    def test_slot_creation(self):
        # Assume function ensure_availability_for_day exists and works as expected
        ensure_availability_for_day(datetime.now().date(), self.category.id)
        self.assertTrue(ReservationSlot.objects.filter(unit=self.unit).exists())

