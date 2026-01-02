"""
Tests for permission classes and role-based access control.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestRoleBasedPermissions:
    """Test role-based access control."""

    def test_admin_can_access_users(self, admin_authenticated_client, teacher_user):
        """Test admin can access user management."""
        url = '/api/users/'
        response = admin_authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_teacher_can_access_students(self, authenticated_client, student):
        """Test teacher can access students."""
        url = '/api/students/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_user_can_access_programs(self, authenticated_client, program):
        """Test authenticated user can access programs."""
        url = '/api/programs/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_user_can_access_sessions(self, authenticated_client, session):
        """Test authenticated user can access sessions."""
        url = '/api/sessions/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_user_can_access_alerts(self, authenticated_client, alert):
        """Test authenticated user can access alerts."""
        url = '/api/alerts/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_swagger_ui_accessible(self, api_client):
        """Test Swagger UI is accessible."""
        url = '/api/docs/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_accessible(self, api_client):
        """Test ReDoc is accessible."""
        url = '/api/redoc/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_schema_accessible(self, api_client):
        """Test OpenAPI schema is accessible."""
        url = '/api/schema/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
