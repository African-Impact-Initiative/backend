import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'venturebuild.settings')
django.setup()

from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from organizations.models import Organization
from unittest.mock import patch
# Retain any additional imports from venturebuild settings if necessary
from venturebuild import settings  

User = get_user_model()

class UserTeamStatusModelTests(TestCase):
    """Test cases for User model team status functionality."""
    
    def setUp(self):
        """Set up test user."""
        self.test_user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_team_status_default_value(self):
        """
        Test that a newly created user has 'ACTIVE' as their default team status.
        """
        self.assertEqual(self.test_user.team_status, 'ACTIVE')

    def test_team_status_valid_choices(self):
        """
        Test that team status can be set to any valid choice.
        """
        valid_statuses = ['ACTIVE', 'VACATION', 'LEAVE']
        
        for status_choice in valid_statuses:
            self.test_user.team_status = status_choice
            self.test_user.save()
            self.assertEqual(
                self.test_user.team_status, 
                status_choice,
                f"Failed to set team status to {status_choice}"
            )

class UserTeamStatusAPITests(APITestCase):
    """Test cases for team status API endpoints."""

    def setUp(self):
        """Set up test user and authentication."""
        # Create primary test user
        self.test_user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Set terms of use acceptance
        self.test_user.terms_of_use = True
        self.test_user.save()
        
        # Create and assign test organization
        self.test_organization = Organization.objects.create(
            name='Test Organization',
            identifier='test-org'
        )
        self.test_user.organization = self.test_organization
        self.test_user.save()
        
        # Set up authentication
        self.client.force_authenticate(user=self.test_user)
        
        # Define API endpoints
        self.personal_info_url = reverse('personal-info')  
        self.team_status_url = reverse('update-team-status')
        self.user_list_url = reverse('user-list')

    def test_update_status_via_personal_info(self):
        """
        Ensure team status can be updated through the personal info endpoint
        along with other user information.
        """
        update_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'Developer',
            'team_status': 'VACATION'
        }
        
        response = self.client.patch(self.personal_info_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.team_status, 'VACATION')
        self.assertEqual(response.data['status'], 'success')

    def test_update_status_directly(self):
        """
        Ensure team status can be updated through the dedicated team status endpoint.
        """
        update_data = {
            'team_status': 'LEAVE'
        }
        
        response = self.client.patch(self.team_status_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.team_status, 'LEAVE')
        self.assertEqual(response.data['status'], 'success')

    def test_reject_invalid_status(self):
        """
        Ensure the API rejects invalid team status values.
        """
        update_data = {
            'team_status': 'INVALID_STATUS'
        }
        
        response = self.client.patch(self.team_status_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_in_user_list(self):
        """
        Ensure team status is included in user list API response.
        """
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data[0] if isinstance(response.data, list) else response.data
        self.assertIn('team_status', user_data)

    def test_unauthorized_status_update(self):
        """
        Ensure unauthorized users cannot update team status.
        """
        # Remove authentication
        self.client.force_authenticate(user=None)
        
        update_data = {
            'team_status': 'VACATION'
        }
        
        response = self.client.patch(self.team_status_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_required_fields(self):
        """
        Ensure API properly handles missing required fields in personal info update.
        """
        incomplete_data = {
            'team_status': 'VACATION'
            # Missing required fields: first_name, last_name, role
        }
        
        response = self.client.patch(self.personal_info_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# The following tests are for Google login functionality.
# Uncomment additional tests as needed.
class GoogleLoginViewTests(TestCase):
    # This sets up the mock data and environment used for conducting the Google auth test
    # cases.
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

    # This test cases for when an invalid token has been sent to the backend for the Google authentication.
    # The main purpose of this is to test whether the endpoint is being called properly. The expected output
    # Should be a 400 error
    @patch('social_django.utils.load_backend')
    @patch('social_django.utils.load_strategy')
    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_google_login_invalid_token(self, mock_load_strategy, mock_load_backend):
        # Mock the backend and strategy
        mock_backend = mock_load_backend.return_value
        mock_strategy = mock_load_strategy.return_value

        # Simulate invalid token scenario
        mock_backend.do_auth.side_effect = Exception("Invalid token")

        # Make a POST request with an invalid token
        response = self.client.post(self.google_login_url, {"token": "invalid_token"})
        print(f"Hello the response is: {response.status_code}")

        # Validate the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Additional test cases can be uncommented and modified as needed.
    # For example:
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

