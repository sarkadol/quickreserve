# Import necessary modules
from django.test import TestCase, Client
from django.urls import reverse

class LoginTestCase(TestCase):
    def setUp(self):
        # Set up data or initialize the test client
        self.client = Client()
        self.csrf_client = Client(enforce_csrf_checks=True)

    def test_login_post(self):
        # Simulate a POST request
        response = self.client.post(reverse('login'), {"username": "john", "password": "smith"})
        self.assertEqual(response.status_code, 200)

    def test_customer_details_get(self):
        # Simulate a GET request
        response = self.client.get(reverse('customer_details'))
        self.assertEqual(response.content, b'<!DOCTYPE html...')

    from django.middleware.csrf import get_token

    def test_csrf_enforced_client(self):
        # First, you might need to perform a get request to retrieve a CSRF token
        response = self.csrf_client.get(reverse('login'))  # Assuming this page has CSRF token
        csrf_token = get_token(response.wsgi_request)

        # Then include this token in your post request
        response = self.csrf_client.post(reverse('login'), {
            "username": "john",
            "password": "smith",
            "csrfmiddlewaretoken": csrf_token
        })
        self.assertEqual(response.status_code, 200)  # Adjust based on expected successful behavior

