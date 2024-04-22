from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from base.models import Offer, Category

class CategoryCreationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='manager', password='test123')
        cls.offer = Offer.objects.create(offer_name="Special Offer", manager_of_this_offer=cls.user)
        cls.category = Category.objects.create(category_name="Deluxe", belongs_to_offer=cls.offer)

   
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

    def test_delete_category(self):
        category_id = self.category.id
        self.client.login(username='manager', password='test123')
        url = reverse('delete_category', args=[self.offer.id, category_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Assuming redirect on success
        self.assertFalse(Category.objects.filter(id=category_id).exists())

    def test_manager_home(self):
        self.client.login(username='manager', password='test123')
        url = reverse('manager_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deluxe")

    def test_my_schedule_view_template_used(self):
        self.client.login(username='manager', password='test123')
        response = self.client.get(reverse('my_schedule'))
        self.assertTemplateUsed(response, 'my_schedule.html')

    """def test_my_schedule_view_context_data(self):
        self.client.login(username='manager', password='test123')
        response = self.client.get(reverse('my_schedule'))
        self.assertIn('categories', response.context)  # Make sure 'categories' is in context
        self.assertIsInstance(response.context['categories'], QuerySet)"""

    def test_my_schedule_view_redirection(self):
        response = self.client.get(reverse('my_schedule'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('my_schedule')}")

    def test_my_schedule_view_unauthorized_access(self):
        # This user does not have permissions or is not logged in
        response = self.client.get(reverse('my_schedule'))
        # Check if there is a redirection to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('my_schedule')}")
