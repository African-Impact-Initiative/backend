from django.test import TestCase
# Create your tests here.

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from organizations.models import Organization

User = get_user_model()

class UserTeamStatusModelTests(TestCase):
    """Test cases for User model team status functionality"""
    
    def setUp(self):
        """Set up test user"""
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
    """Test cases for team status API endpoints"""

    def setUp(self):
        """Set up test user and authentication"""
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