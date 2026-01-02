"""
Tests for Authentication API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationEndpoints:
    """Test authentication endpoints."""

    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@spas.ca',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'teacher'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == 'newuser@spas.ca'

    def test_register_user_password_mismatch(self, api_client):
        """Test registration fails with password mismatch."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@spas.ca',
            'password': 'SecurePassword123!',
            'password_confirm': 'DifferentPassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'teacher'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_email(self, api_client, teacher_user):
        """Test registration fails with duplicate email."""
        url = '/api/auth/register/'
        data = {
            'email': teacher_user.email,
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'teacher'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, api_client, teacher_user):
        """Test successful login."""
        url = '/api/auth/login/'
        data = {
            'email': teacher_user.email,
            'password': 'teacher123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_login_invalid_credentials(self, api_client, teacher_user):
        """Test login fails with invalid credentials."""
        url = '/api/auth/login/'
        data = {
            'email': teacher_user.email,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self, api_client, create_user):
        """Test login fails for inactive user."""
        inactive_user = create_user(
            email='inactive@spas.ca',
            password='testpassword',
            is_active=False
        )
        url = '/api/auth/login/'
        data = {
            'email': inactive_user.email,
            'password': 'testpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        # First get a refresh token
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email='teacher@spas.ca')
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        url = '/api/auth/logout/'
        data = {'refresh': str(refresh)}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_token_refresh(self, api_client, teacher_user):
        """Test token refresh."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(teacher_user)
        
        url = '/api/auth/token/refresh/'
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_current_user(self, authenticated_client):
        """Test getting current user info."""
        url = '/api/auth/me/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'email' in response.data

    def test_change_password_success(self, authenticated_client, teacher_user):
        """Test successful password change."""
        url = '/api/auth/password/change/'
        data = {
            'old_password': 'teacher123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_access_denied(self, api_client):
        """Test unauthenticated access is denied to protected endpoints."""
        url = '/api/auth/me/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
