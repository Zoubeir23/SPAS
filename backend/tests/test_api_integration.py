"""
Tests d'intégration API pour SPAS.

Ces tests vérifient les endpoints critiques de l'API Django REST Framework.
Usage: pytest tests/test_api_integration.py -v
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.students.models import Student
from apps.programs.models import Program, Subject
from apps.sessions.models import Session
from apps.grades.models import Grade
from apps.attendance.models import Attendance
from apps.alerts.models import Alert, Intervention
from apps.predictions.models import Prediction
from apps.ml.models import MLModel
from datetime import date, timedelta, datetime
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


@pytest.fixture
def api_client():
    """Crée un client API non authentifié."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Crée un utilisateur admin pour les tests."""
    user = User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        first_name='Admin',
        last_name='Test',
        role=User.Role.ADMIN,
        is_staff=True,
    )
    return user


@pytest.fixture
def teacher_user(db):
    """Crée un utilisateur enseignant pour les tests."""
    user = User.objects.create_user(
        email='teacher@test.com',
        password='testpass123',
        first_name='Teacher',
        last_name='Test',
        role=User.Role.TEACHER,
    )
    return user


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Crée un client API authentifié comme admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def program(db):
    """Crée un programme de test."""
    return Program.objects.create(
        name='Test Program',
        code='TEST-001',
        duration=3,
        status='active'
    )


@pytest.fixture
def session(db):
    """Crée une session académique de test."""
    return Session.objects.create(
        name='2025-2026',
        year='2025',
        start_date=date(2025, 10, 1),
        end_date=date(2026, 6, 30),
        status='active'
    )


@pytest.fixture
def subject(db):
    """Crée une matière de test."""
    return Subject.objects.create(
        name='Test Subject',
        code='SUBJ-001'
    )


@pytest.fixture
def student(db, program, session):
    """Crée un étudiant de test."""
    return Student.objects.create(
        matricule='TEST001',
        first_name='Test',
        last_name='Student',
        email='student@test.com',
        date_of_birth=date(2000, 1, 1),
        program=program,
        session=session,
        status='active',
        risk_level='low'
    )


# ============================================================================
# Tests d'Authentification
# ============================================================================

@pytest.mark.django_db
class TestAuthentication:
    """Tests pour l'authentification JWT."""

    def test_login_success(self, api_client, admin_user):
        """Test de connexion réussie."""
        url = '/api/auth/login/'
        response = api_client.post(url, {
            'email': 'admin@test.com',
            'password': 'testpass123'
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_login_wrong_password(self, api_client, admin_user):
        """Test de connexion avec mauvais mot de passe."""
        url = '/api/auth/login/'
        response = api_client.post(url, {
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        }, format='json')
        
        # L'API retourne 400 Bad Request pour les identifiants invalides
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, api_client):
        """Test de connexion avec utilisateur inexistant."""
        url = '/api/auth/login/'
        response = api_client.post(url, {
            'email': 'nonexistent@test.com',
            'password': 'testpass123'
        }, format='json')
        
        # L'API retourne 400 Bad Request pour les identifiants invalides
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_protected_endpoint_without_auth(self, api_client):
        """Test d'accès à un endpoint protégé sans authentification."""
        url = '/api/students/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Tests des Étudiants
# ============================================================================

@pytest.mark.django_db
class TestStudentAPI:
    """Tests pour l'API des étudiants."""

    def test_list_students(self, authenticated_client, student):
        """Test de la liste des étudiants."""
        url = '/api/students/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1

    def test_retrieve_student(self, authenticated_client, student):
        """Test de récupération d'un étudiant."""
        url = f'/api/students/{student.id}/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['matricule'] == 'TEST001'
        assert response.data['first_name'] == 'Test'

    def test_create_student(self, authenticated_client, program, session):
        """Test de création d'un étudiant."""
        url = '/api/students/'
        data = {
            'matricule': 'NEW001',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'new@test.com',
            'date_of_birth': '2000-05-15',
            'program': program.id,
            'session': session.id,
            'status': 'active'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Student.objects.filter(matricule='NEW001').exists()

    def test_update_student(self, authenticated_client, student):
        """Test de mise à jour d'un étudiant."""
        url = f'/api/students/{student.id}/'
        data = {'first_name': 'Updated'}
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.first_name == 'Updated'

    def test_filter_students_by_risk(self, authenticated_client, student):
        """Test du filtre par niveau de risque."""
        url = '/api/students/?risk_level=low'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        for s in response.data['results']:
            assert s['risk_level'] == 'low'

    def test_search_students(self, authenticated_client, student):
        """Test de la recherche d'étudiants."""
        url = '/api/students/?search=Test'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


# ============================================================================
# Tests des Programmes
# ============================================================================

@pytest.mark.django_db
class TestProgramAPI:
    """Tests pour l'API des programmes."""

    def test_list_programs(self, authenticated_client, program):
        """Test de la liste des programmes."""
        url = '/api/programs/programs/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_create_program(self, authenticated_client):
        """Test de création d'un programme."""
        url = '/api/programs/programs/'
        data = {
            'name': 'New Program',
            'code': 'NEW-001',
            'duration': 2,
            'status': 'active'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED


# ============================================================================
# Tests des Notes
# ============================================================================

@pytest.mark.django_db
class TestGradeAPI:
    """Tests pour l'API des notes."""

    def test_create_grade(self, authenticated_client, student, subject, session):
        """Test de création d'une note."""
        url = '/api/grades/grades/'
        data = {
            'student': student.id,
            'subject': subject.id,
            'session': session.id,
            'value': 15.5,
            'max_value': 20,
            'type': 'exam',
            'date': str(date.today())
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Grade.objects.filter(student=student, subject=subject).exists()

    def test_list_student_grades(self, authenticated_client, student, subject, session):
        """Test de la liste des notes d'un étudiant."""
        # Créer une note
        Grade.objects.create(
            student=student,
            subject=subject,
            session=session,
            value=Decimal('15.0'),
            max_value=Decimal('20'),
            type='exam',
            date=date.today()
        )
        
        url = f'/api/students/{student.id}/grades/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Tests des Présences
# ============================================================================

@pytest.mark.django_db
class TestAttendanceAPI:
    """Tests pour l'API des présences."""

    def test_create_attendance(self, authenticated_client, student, subject):
        """Test de création d'une présence."""
        url = '/api/attendance/attendance/'
        data = {
            'student': student.id,
            'subject': subject.id,
            'date': str(date.today()),
            'status': 'present'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_student_attendance(self, authenticated_client, student, subject):
        """Test de la liste des présences d'un étudiant."""
        # Créer une présence
        Attendance.objects.create(
            student=student,
            subject=subject,
            date=date.today(),
            status='present'
        )
        
        url = f'/api/students/{student.id}/attendance/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Tests des Alertes
# ============================================================================

@pytest.mark.django_db
class TestAlertAPI:
    """Tests pour l'API des alertes."""

    def test_list_alerts(self, authenticated_client, student):
        """Test de la liste des alertes."""
        Alert.objects.create(
            student=student,
            type='risk',
            level='medium',
            status='new',
            message='Test alert'
        )
        
        url = '/api/alerts/alerts/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_acknowledge_alert(self, authenticated_client, student):
        """Test d'accusé de réception d'une alerte."""
        alert = Alert.objects.create(
            student=student,
            type='risk',
            level='medium',
            status='new',
            message='Test alert'
        )
        
        url = f'/api/alerts/alerts/{alert.id}/acknowledge/'
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        alert.refresh_from_db()
        assert alert.status == 'acknowledged'

    def test_resolve_alert(self, authenticated_client, student):
        """Test de résolution d'une alerte."""
        alert = Alert.objects.create(
            student=student,
            type='risk',
            level='medium',
            status='acknowledged',
            message='Test alert'
        )
        
        url = f'/api/alerts/alerts/{alert.id}/resolve/'
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        alert.refresh_from_db()
        assert alert.status == 'resolved'


# ============================================================================
# Tests des Interventions
# ============================================================================

@pytest.mark.django_db
class TestInterventionAPI:
    """Tests pour l'API des interventions."""

    def test_create_intervention(self, authenticated_client, student):
        """Test de création d'une intervention."""
        url = '/api/alerts/interventions/'
        data = {
            'student': student.id,
            'type': 'meeting',
            'priority': 'medium',
            'description': 'Test intervention',
            'scheduled_date': str(date.today() + timedelta(days=7))
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Intervention.objects.filter(student=student).exists()

    def test_complete_intervention(self, authenticated_client, student, admin_user):
        """Test de complétion d'une intervention."""
        intervention = Intervention.objects.create(
            student=student,
            type='meeting',
            priority='medium',
            status='planned',
            description='Test',
            scheduled_date=date.today(),
            responsible=admin_user
        )
        
        url = f'/api/alerts/interventions/{intervention.id}/complete/'
        response = authenticated_client.post(url, {'outcome': 'Completed successfully'})
        
        assert response.status_code == status.HTTP_200_OK
        intervention.refresh_from_db()
        assert intervention.status == 'completed'


# ============================================================================
# Tests des Prédictions
# ============================================================================

@pytest.mark.django_db
class TestPredictionAPI:
    """Tests pour l'API des prédictions."""

    def test_list_predictions(self, authenticated_client, student):
        """Test de la liste des prédictions."""
        Prediction.objects.create(
            student=student,
            risk_score=45,
            risk_level='medium',
            predicted_success_rate=55,
            factors=[{'name': 'attendance', 'impact': 0.3}]
        )
        
        url = '/api/predictions/predictions/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_filter_high_risk_predictions(self, authenticated_client, student):
        """Test du filtre des prédictions à haut risque."""
        Prediction.objects.create(
            student=student,
            risk_score=80,
            risk_level='critical',
            predicted_success_rate=20,
            factors=[]
        )
        
        # Utiliser le filtre plutôt qu'une action personnalisée
        url = '/api/predictions/predictions/?risk_level=critical'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Tests des Modèles ML
# ============================================================================

@pytest.mark.django_db
class TestMLModelAPI:
    """Tests pour l'API des modèles ML."""

    def test_list_models(self, authenticated_client):
        """Test de la liste des modèles."""
        MLModel.objects.create(
            name='Test Model',
            version='1.0.0',
            status='active',
            accuracy=Decimal('85.0'),
            precision=Decimal('80.0'),
            recall=Decimal('82.0'),
            f1_score=Decimal('81.0'),
            training_data_size=1000,
            trained_at=timezone.now()
        )
        
        url = '/api/ml/models/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_active_model(self, authenticated_client):
        """Test de récupération du modèle actif."""
        MLModel.objects.create(
            name='Active Model',
            version='1.0.0',
            status='active',
            accuracy=Decimal('90.0'),
            precision=Decimal('88.0'),
            recall=Decimal('87.0'),
            f1_score=Decimal('87.5'),
            training_data_size=2000,
            trained_at=timezone.now()
        )
        
        url = '/api/ml/models/active/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Tests des Utilisateurs
# ============================================================================

@pytest.mark.django_db
class TestUserAPI:
    """Tests pour l'API des utilisateurs."""

    def test_list_users(self, authenticated_client, admin_user):
        """Test de la liste des utilisateurs."""
        url = '/api/users/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_current_user(self, authenticated_client, admin_user):
        """Test de récupération de l'utilisateur courant."""
        url = '/api/users/me/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'admin@test.com'

    def test_create_user(self, authenticated_client):
        """Test de création d'un utilisateur."""
        url = '/api/users/'
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'teacher'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@test.com').exists()
