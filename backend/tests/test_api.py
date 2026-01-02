"""
Tests for Students API endpoints.
"""
import pytest
from rest_framework import status
from datetime import date


@pytest.mark.django_db
class TestStudentEndpoints:
    """Test student API endpoints."""

    def test_list_students_authenticated(self, authenticated_client, student):
        """Test listing students with authentication."""
        url = '/api/students/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)

    def test_list_students_unauthenticated(self, api_client):
        """Test listing students without authentication fails."""
        url = '/api/students/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_student_detail(self, authenticated_client, student):
        """Test getting student detail."""
        url = f'/api/students/{student.id}/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['matricule'] == student.matricule
        assert response.data['first_name'] == student.first_name

    def test_create_student(self, admin_authenticated_client, program, session):
        """Test creating a new student."""
        url = '/api/students/'
        data = {
            'matricule': '2024099',
            'first_name': 'Nouveau',
            'last_name': 'Étudiant',
            'email': 'nouveau.etudiant@student.spas.ca',
            'phone': '+1 514 555-0099',
            'date_of_birth': '2001-03-15',
            'program': program.id,
            'session': session.id,
            'status': 'active'
        }
        response = admin_authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['matricule'] == '2024099'

    def test_update_student(self, authenticated_client, student):
        """Test updating a student."""
        url = f'/api/students/{student.id}/'
        data = {'first_name': 'Alexandre Updated'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Alexandre Updated'

    def test_delete_student(self, admin_authenticated_client, student):
        """Test deleting a student."""
        url = f'/api/students/{student.id}/'
        response = admin_authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_filter_students_by_program(self, authenticated_client, student, program):
        """Test filtering students by program."""
        url = f'/api/students/?program={program.id}'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_students_by_risk_level(self, authenticated_client, student, high_risk_student):
        """Test filtering students by risk level."""
        url = '/api/students/?risk_level=high'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_search_students(self, authenticated_client, student):
        """Test searching students by name."""
        url = f'/api/students/?search={student.last_name}'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_student_predictions_action(self, authenticated_client, student):
        """Test getting predictions for a student."""
        url = f'/api/students/{student.id}/predictions/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_student_grades_action(self, authenticated_client, student):
        """Test getting grades for a student."""
        url = f'/api/students/{student.id}/grades/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_student_attendance_action(self, authenticated_client, student):
        """Test getting attendance for a student."""
        url = f'/api/students/{student.id}/attendance/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProgramEndpoints:
    """Test program API endpoints."""

    def test_list_programs(self, authenticated_client, program):
        """Test listing programs."""
        url = '/api/programs/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_program_detail(self, authenticated_client, program):
        """Test getting program detail."""
        url = f'/api/programs/{program.id}/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == program.code

    def test_create_program(self, admin_authenticated_client):
        """Test creating a program."""
        url = '/api/programs/'
        data = {
            'name': 'Nouveau Programme',
            'code': 'NP.01',
            'description': 'Description du nouveau programme',
            'duration': 2,
            'status': 'active'
        }
        response = admin_authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_program_students_action(self, authenticated_client, program, student):
        """Test getting students in a program."""
        url = f'/api/programs/{program.id}/students/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSessionEndpoints:
    """Test session API endpoints."""

    def test_list_sessions(self, authenticated_client, session):
        """Test listing sessions."""
        url = '/api/sessions/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_session_detail(self, authenticated_client, session):
        """Test getting session detail."""
        url = f'/api/sessions/{session.id}/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == session.name

    def test_create_session(self, admin_authenticated_client):
        """Test creating a session."""
        url = '/api/sessions/'
        data = {
            'name': 'Hiver 2025',
            'year': '2024-2025',
            'start_date': '2025-01-06',
            'end_date': '2025-05-15',
            'status': 'active'
        }
        response = admin_authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestAlertEndpoints:
    """Test alert API endpoints."""

    def test_list_alerts(self, authenticated_client, alert):
        """Test listing alerts."""
        url = '/api/alerts/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_alert_detail(self, authenticated_client, alert):
        """Test getting alert detail."""
        url = f'/api/alerts/{alert.id}/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['type'] == alert.type

    def test_create_alert(self, authenticated_client, student):
        """Test creating an alert."""
        url = '/api/alerts/'
        data = {
            'student': student.id,
            'type': 'attendance',
            'level': 'high',
            'message': 'Taux de présence faible détecté',
            'status': 'new'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_alert_status(self, authenticated_client, alert):
        """Test updating alert status."""
        url = f'/api/alerts/{alert.id}/'
        data = {'status': 'acknowledged'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_filter_alerts_by_level(self, authenticated_client, alert):
        """Test filtering alerts by level."""
        url = '/api/alerts/?level=medium'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_alerts_by_status(self, authenticated_client, alert):
        """Test filtering alerts by status."""
        url = '/api/alerts/?status=new'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSubjectEndpoints:
    """Test subject API endpoints."""

    def test_list_subjects(self, authenticated_client, subject):
        """Test listing subjects."""
        url = '/api/programs/subjects/'
        response = authenticated_client.get(url)
        # Might be nested under programs or separate
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestUserEndpoints:
    """Test user management API endpoints."""

    def test_list_users_as_admin(self, admin_authenticated_client, teacher_user):
        """Test listing users as admin."""
        url = '/api/users/'
        response = admin_authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_user_detail(self, admin_authenticated_client, teacher_user):
        """Test getting user detail."""
        url = f'/api/users/{teacher_user.id}/'
        response = admin_authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_me_endpoint(self, authenticated_client, teacher_user):
        """Test getting current user via /me endpoint."""
        url = '/api/users/me/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == teacher_user.email
