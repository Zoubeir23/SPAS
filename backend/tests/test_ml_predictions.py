"""
Tests for ML and Predictions API endpoints.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestMLModelEndpoints:
    """Test ML model API endpoints."""

    def test_list_ml_models(self, authenticated_client):
        """Test listing ML models."""
        url = '/api/ml/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_ml_models_unauthenticated(self, api_client):
        """Test listing ML models without authentication fails."""
        url = '/api/ml/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPredictionEndpoints:
    """Test prediction API endpoints."""

    def test_list_predictions(self, authenticated_client):
        """Test listing predictions."""
        url = '/api/predictions/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_predictions_unauthenticated(self, api_client):
        """Test listing predictions without authentication fails."""
        url = '/api/predictions/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGradeEndpoints:
    """Test grade API endpoints."""

    def test_list_grades(self, authenticated_client):
        """Test listing grades."""
        url = '/api/grades/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestAttendanceEndpoints:
    """Test attendance API endpoints."""

    def test_list_attendance(self, authenticated_client):
        """Test listing attendance records."""
        url = '/api/attendance/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
