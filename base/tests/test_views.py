from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from base.models import Offer, Category

class CategoryCreationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='manager', password='test123')
        cls.offer = Offer.objects.create(offer_name="Special Offer", manager_of_this_offer=cls.user)

    def test_create_category_with_valid_data(self):
        self.client.login(username='manager', password='test123')
        url = reverse('create_category', args=[self.offer.id])
        response = self.client.post(url, {
            'category_name': 'Deluxe Rooms',
            'category_description': 'Spacious and luxurious rooms with sea view',
            'belongs_to_offer': self.offer.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(category_name='Deluxe Rooms').exists())
        category = Category.objects.get(category_name='Deluxe Rooms')
        self.assertEqual(category.category_description, 'Spacious and luxurious rooms with sea view')

    def test_create_category_with_missing_fields(self):
        self.client.login(username='manager', password='test123')
        url = reverse('create_category', args=[self.offer.id])
        response = self.client.post(url, {
            # Missing 'category_name'
            'category_description': 'Incomplete data',
            'belongs_to_offer': self.offer.id,
        })
        self.assertEqual(response.status_code, 200)  # Expecting failure to redirect due to form errors
        self.assertFalse(Category.objects.filter(category_description='Incomplete data').exists())
