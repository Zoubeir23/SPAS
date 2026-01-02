"""
Tests for authentication functionality.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import User


class LoginTestCase(APITestCase):
    """Tests for login endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')

        # Create test user
        self.user = User.objects.create_user(
            email='teacher@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

    def test_login_success(self):
        """Test successful login."""
        data = {
            'email': 'teacher@test.com',
            'password': 'TestPass123!'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'teacher@test.com')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'email': 'teacher@test.com',
            'password': 'WrongPassword'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)

    def test_login_inactive_user(self):
        """Test login with inactive user."""
        self.user.is_active = False
        self.user.save()

        data = {
            'email': 'teacher@test.com',
            'password': 'TestPass123!'
        }

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        # Missing password
        response = self.client.post(
            self.login_url,
            {'email': 'teacher@test.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing email
        response = self.client.post(
            self.login_url,
            {'password': 'TestPass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshTestCase(APITestCase):
    """Tests for token refresh endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')
        self.refresh_url = reverse('authentication:token_refresh')

        # Create test user and get tokens
        self.user = User.objects.create_user(
            email='teacher@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

        login_response = self.client.post(
            self.login_url,
            {
                'email': 'teacher@test.com',
                'password': 'TestPass123!'
            },
            format='json'
        )
        self.refresh_token = login_response.data['refresh']

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        response = self.client.post(
            self.refresh_url,
            {'refresh': self.refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_invalid(self):
        """Test token refresh with invalid token."""
        response = self.client.post(
            self.refresh_url,
            {'refresh': 'invalid_token'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTestCase(APITestCase):
    """Tests for logout endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')

        # Create test user and login
        self.user = User.objects.create_user(
            email='teacher@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

        login_response = self.client.post(
            self.login_url,
            {
                'email': 'teacher@test.com',
                'password': 'TestPass123!'
            },
            format='json'
        )
        self.access_token = login_response.data['access']
        self.refresh_token = login_response.data['refresh']

    def test_logout_success(self):
        """Test successful logout."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.post(
            self.logout_url,
            {'refresh': self.refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_without_authentication(self):
        """Test logout without authentication."""
        response = self.client.post(
            self.logout_url,
            {'refresh': self.refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetTestCase(APITestCase):
    """Tests for password reset functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.reset_request_url = reverse('authentication:password_reset_request')
        self.reset_confirm_url = reverse('authentication:password_reset_confirm')

        # Create test user
        self.user = User.objects.create_user(
            email='teacher@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

    def test_password_reset_request_success(self):
        """Test password reset request with valid email."""
        response = self.client.post(
            self.reset_request_url,
            {'email': 'teacher@test.com'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email."""
        response = self.client.post(
            self.reset_request_url,
            {'email': 'nonexistent@test.com'},
            format='json'
        )

        # Should still return 200 for security (don't reveal email existence)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirm with invalid token."""
        response = self.client.post(
            self.reset_confirm_url,
            {
                'uid': 'invalid_uid',
                'token': 'invalid_token',
                'new_password': 'NewPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordTestCase(APITestCase):
    """Tests for password change functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')
        self.change_password_url = reverse('authentication:change_password')

        # Create test user and login
        self.user = User.objects.create_user(
            email='teacher@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

        login_response = self.client.post(
            self.login_url,
            {
                'email': 'teacher@test.com',
                'password': 'TestPass123!'
            },
            format='json'
        )
        self.access_token = login_response.data['access']

    def test_change_password_success(self):
        """Test successful password change."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'TestPass123!',
                'new_password': 'NewPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        login_response = self.client.post(
            self.login_url,
            {
                'email': 'teacher@test.com',
                'password': 'NewPass123!'
            },
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'WrongPassword',
                'new_password': 'NewPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_without_authentication(self):
        """Test password change without authentication."""
        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'TestPass123!',
                'new_password': 'NewPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CurrentUserTestCase(APITestCase):
    """Tests for current user endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')
        self.current_user_url = reverse('authentication:current_user')

        # Create test user and login
        self.user = User.objects.create_user(
            email='teacher@test.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Teacher',
            role='teacher'
        )

        login_response = self.client.post(
            self.login_url,
            {
                'email': 'teacher@test.com',
                'password': 'TestPass123!'
            },
            format='json'
        )
        self.access_token = login_response.data['access']

    def test_current_user_success(self):
        """Test getting current user data."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'teacher@test.com')
        self.assertEqual(response.data['role'], 'teacher')

    def test_current_user_without_authentication(self):
        """Test getting current user without authentication."""
        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
