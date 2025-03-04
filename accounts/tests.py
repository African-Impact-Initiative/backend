import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'venturebuild.settings')
django.setup()

from django.test import TestCase
from django.conf import settings

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth.models import User

from venturebuild import settings

User = get_user_model()


# Create your tests here.
# class LoginTestCase(TestCase):
#     def setUp(self):
#         self.password = 'test1234'
#         self.email = 'bowale.adetunji@mail.utoronto.ca'  #Test email
#         self.user, created = User.objects.get_or_create(
#             email=self.email,
#             defaults={'password': self.password, 'first_name': 'test', 'last_name': '1'}
#         )
#
#     # def test_login(self):
#     #     login_url = '/login/'
#     #     response = self.client.post(login_url, {'email': self.email, 'password': self.password})
#     #
#     #     self.assertEquals(response.status_code, 200)
#     #     self.assertTrue(response.url, reverse('home'))
#     #     self.assertTrue(self.client.login(email=self.email, password=self.password))
#
#     @override_settings(ALLOWED_HOSTS=['testserver'])
#     class MyTestCase(TestCase):
#         def test_login_view(self):
#             response = self.client.post('/login/', {'username': 'test', 'password': 'test'})
#             self.assertEqual(response.status_code, 200)


class GoogleLoginViewTests(TestCase):
    def setUp(self):
        # Initialize the test client
        self.client = APIClient()

        # Define the endpoint
        self.google_login_url = reverse('google-login')

        # Mock data
        self.mock_token = "mock_google_token"
        self.mock_user_data = {
            "id": "123456789",
            "email": "testuser@example.com",
            "name": "Test User",
        }

    @patch('social_django.utils.load_backend')
    @patch('social_django.utils.load_strategy')
    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_google_login_invalid_token(self, mock_load_strategy, mock_load_backend):
        # Mock the backend and strategy
        mock_backend = mock_load_backend.return_value
        mock_strategy = mock_load_strategy.return_value

        # Simulate invalid token scenario
        mock_backend.do_auth.side_effect = Exception("Invalid token")

        # Make a POST request with invalid token
        response = self.client.post(self.google_login_url, {"token": "invalid_token"})
        print(f"Hello the response is: {response.status_code}")

        # Validate the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('error', response.data)

    # def test_google_login_missing_token(self):
    #     # Make a POST request without an access token
    #     response = self.client.post(self.google_login_url, {})
    #
    #     # Validate the response
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('error', response.data)

    # @patch('social_django.utils.load_backend')
    # @patch('social_django.utils.load_strategy')
    # @override_settings(ALLOWED_HOSTS=['testserver'])
    # def test_google_login_success(self, mock_load_strategy, mock_load_backend):
    #     # Mock the backend and strategy
    #     mock_backend = mock_load_backend.return_value
    #     mock_strategy = mock_load_strategy.return_value
    #
    #     # Mock successful user authentication
    #     mock_backend.do_auth.return_value = User.objects.create_user(
    #         email=self.mock_user_data["email"],
    #         password="testpassword",  # Required if your custom model has password validation
    #         first_name="Test",
    #         last_name="User"
    #     )
    #
    #     # Make a POST request to the endpoint
    #     response = self.client.post(self.google_login_url, {"access_token": self.mock_token})
    #
    #     # Validate the response
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('token', response.data)

    # @patch('social_django.utils.load_backend')
    # @patch('social_django.utils.load_strategy')
    # @override_settings(ALLOWED_HOSTS=['testserver'])
    # def test_google_login_user_creation(self, mock_load_strategy, mock_load_backend):
    #     # Mock the backend and strategy
    #     mock_backend = mock_load_backend.return_value
    #     #mock_strategy = mock_load_strategy.return_value
    #
    #     # Mock successful user authentication
    #     mock_backend.do_auth.return_value = User.objects.create(
    #         first_name="newuser",
    #         last_name="last_name",
    #         email="newuser@example.com"
    #     )
    #
    #     # Make a POST request to the endpoint
    #     response = self.client.post(self.google_login_url, {"access_token": self.mock_token})
    #
    #     # Validate the response
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(User.objects.filter(email="newuser@example.com").exists())
    #     self.assertIn('token', response.data)
    #
