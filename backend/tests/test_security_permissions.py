"""
Tests de sécurité pour le contrôle d'accès basé sur les rôles.

Couvre :
- teacher_can_access_student()
- AlertViewSet : filtrage queryset par rôle, IDOR sur student_alerts
- InterventionViewSet : filtrage queryset par rôle, IDOR sur student_interventions
- PredictionViewSet : IDOR sur student_predictions
- register_view : absence de verification_token dans la réponse
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def program(db):
    from apps.programs.models import Program
    return Program.objects.create(
        name='Informatique', code='420.B0', duration=3, status='active'
    )


@pytest.fixture
def session_obj(db):
    from apps.sessions.models import Session
    from datetime import date
    return Session.objects.create(
        name='Automne 2024', year='2024-2025',
        start_date=date(2024, 9, 1), end_date=date(2024, 12, 20),
        status='active'
    )


@pytest.fixture
def teacher(db):
    return User.objects.create_user(
        email='teacher@test.ca', password='pass1234!',
        first_name='Jean', last_name='Prof', role='teacher', is_active=True
    )


@pytest.fixture
def other_teacher(db):
    return User.objects.create_user(
        email='other@test.ca', password='pass1234!',
        first_name='Marie', last_name='Autre', role='teacher', is_active=True
    )


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email='admin@test.ca', password='pass1234!',
        first_name='Admin', last_name='Super', role='admin',
        is_active=True, is_staff=True, is_superuser=True
    )


@pytest.fixture
def pedagogical(db):
    return User.objects.create_user(
        email='peda@test.ca', password='pass1234!',
        first_name='Peda', last_name='User', role='pedagogical', is_active=True
    )


@pytest.fixture
def student_a(db, program, session_obj):
    from apps.students.models import Student
    from datetime import date
    return Student.objects.create(
        matricule='A001', first_name='Alice', last_name='Martin',
        email='alice@student.ca', date_of_birth=date(2000, 1, 1),
        program=program, session=session_obj, status='active'
    )


@pytest.fixture
def student_b(db, program, session_obj):
    from apps.students.models import Student
    from datetime import date
    return Student.objects.create(
        matricule='B002', first_name='Bob', last_name='Dupont',
        email='bob@student.ca', date_of_birth=date(2001, 2, 2),
        program=program, session=session_obj, status='active'
    )


@pytest.fixture
def alert_a(db, student_a):
    from apps.alerts.models import Alert
    return Alert.objects.create(
        student=student_a, type='performance', level='medium',
        message='Alerte pour Alice', status='new'
    )


@pytest.fixture
def alert_b(db, student_b):
    from apps.alerts.models import Alert
    return Alert.objects.create(
        student=student_b, type='performance', level='high',
        message='Alerte pour Bob', status='new'
    )


@pytest.fixture
def intervention_a(db, student_a):
    from apps.alerts.models import Intervention
    from datetime import date
    return Intervention.objects.create(
        student=student_a, type='academic', priority='medium',
        description='Intervention Alice', scheduled_date=date(2024, 10, 1)
    )


@pytest.fixture
def intervention_b(db, student_b):
    from apps.alerts.models import Intervention
    from datetime import date
    return Intervention.objects.create(
        student=student_b, type='academic', priority='high',
        description='Intervention Bob', scheduled_date=date(2024, 10, 2)
    )


# ---------------------------------------------------------------------------
# Tests : teacher_can_access_student
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTeacherCanAccessStudent:
    """Vérifie la logique de la fonction helper teacher_can_access_student."""

    def test_admin_not_a_teacher(self, admin, student_a):
        """Les admins passent par has_elevated_permissions, pas ce helper."""
        from apps.core.permissions import teacher_can_access_student
        # Le helper ne doit pas être appelé pour les admins, mais s'il l'est
        # il retourne False car admin n'est pas lié à l'étudiant comme enseignant
        result = teacher_can_access_student(admin, student_a)
        # Pas de teacher FK → utilise enrollments → aucune inscription → False
        assert result is False

    def test_teacher_without_link_cannot_access(self, teacher, student_a):
        """Un enseignant sans lien avec l'étudiant est refusé."""
        from apps.core.permissions import teacher_can_access_student
        result = teacher_can_access_student(teacher, student_a)
        assert result is False

    def test_fail_closed_no_enrollments(self, teacher, student_a):
        """Sans inscriptions, l'accès est refusé (fail-closed)."""
        from apps.core.permissions import teacher_can_access_student
        # student_a n'a aucune inscription → doit retourner False
        assert teacher_can_access_student(teacher, student_a) is False


# ---------------------------------------------------------------------------
# Tests : AlertViewSet — filtrage queryset par rôle
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAlertViewSetQuerysetScoping:
    """Un enseignant ne doit voir que les alertes de ses propres étudiants."""

    def test_admin_sees_all_alerts(self, admin, alert_a, alert_b):
        """Un admin voit toutes les alertes."""
        client = auth_client(admin)
        resp = client.get('/api/alerts/alerts/')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data
        items = data.get('results', data) if isinstance(data, dict) else data
        ids = [str(a['id']) for a in items]
        assert str(alert_a.id) in ids
        assert str(alert_b.id) in ids

    def test_pedagogical_sees_all_alerts(self, pedagogical, alert_a, alert_b):
        """Un conseiller pédagogique voit toutes les alertes."""
        client = auth_client(pedagogical)
        resp = client.get('/api/alerts/alerts/')
        assert resp.status_code == status.HTTP_200_OK

    def test_teacher_without_students_sees_no_alerts(self, teacher, alert_a, alert_b):
        """Un enseignant sans étudiants assignés ne voit aucune alerte."""
        client = auth_client(teacher)
        resp = client.get('/api/alerts/alerts/')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data
        count = data.get('count', len(data.get('results', data))) if isinstance(data, dict) else len(data)
        assert count == 0


# ---------------------------------------------------------------------------
# Tests : AlertViewSet — student_alerts IDOR
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentAlertsIDOR:
    """Vérifie qu'un enseignant ne peut pas accéder aux alertes d'un étudiant non assigné."""

    def test_teacher_cannot_access_unassigned_student_alerts(self, teacher, student_a, alert_a):
        """403 pour un enseignant qui n'a pas accès à cet étudiant."""
        client = auth_client(teacher)
        resp = client.get(f'/api/alerts/alerts/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_access_any_student_alerts(self, admin, student_a, alert_a):
        """Un admin peut accéder aux alertes de n'importe quel étudiant."""
        client = auth_client(admin)
        resp = client.get(f'/api/alerts/alerts/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_access_student_alerts(self, student_a, alert_a):
        """Un utilisateur non authentifié reçoit 401."""
        client = APIClient()
        resp = client.get(f'/api/alerts/alerts/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_student_not_found_returns_404(self, admin):
        """Un ID étudiant inexistant retourne 404."""
        client = auth_client(admin)
        resp = client.get('/api/alerts/alerts/student/99999999/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Tests : InterventionViewSet — student_interventions IDOR
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentInterventionsIDOR:
    """Vérifie qu'un enseignant ne peut pas accéder aux interventions d'un étudiant non assigné."""

    def test_teacher_cannot_access_unassigned_student_interventions(
        self, teacher, student_a, intervention_a
    ):
        """403 pour un enseignant qui n'a pas accès à cet étudiant."""
        client = auth_client(teacher)
        resp = client.get(f'/api/alerts/interventions/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_access_any_student_interventions(self, admin, student_a, intervention_a):
        """Un admin peut accéder aux interventions de n'importe quel étudiant."""
        client = auth_client(admin)
        resp = client.get(f'/api/alerts/interventions/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_200_OK

    def test_teacher_queryset_scoped_to_own_students(
        self, teacher, intervention_a, intervention_b
    ):
        """Un enseignant sans étudiants voit 0 interventions."""
        client = auth_client(teacher)
        resp = client.get('/api/alerts/interventions/')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data
        count = data.get('count', len(data.get('results', data))) if isinstance(data, dict) else len(data)
        assert count == 0


# ---------------------------------------------------------------------------
# Tests : PredictionViewSet — student_predictions IDOR
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStudentPredictionsIDOR:
    """Vérifie qu'un enseignant ne peut pas accéder aux prédictions d'un étudiant non assigné."""

    def test_teacher_cannot_access_unassigned_student_predictions(self, teacher, student_a):
        """403 pour un enseignant qui n'a pas accès à cet étudiant."""
        client = auth_client(teacher)
        resp = client.get(f'/api/predictions/predictions/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_access_any_student_predictions(self, admin, student_a):
        """Un admin peut accéder aux prédictions de n'importe quel étudiant."""
        client = auth_client(admin)
        resp = client.get(f'/api/predictions/predictions/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_200_OK

    def test_invalid_student_id_returns_404(self, admin):
        """Un ID étudiant inexistant retourne 404."""
        client = auth_client(admin)
        resp = client.get('/api/predictions/predictions/student/99999999/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_cannot_access_predictions(self, student_a):
        """Un utilisateur non authentifié reçoit 401."""
        client = APIClient()
        resp = client.get(f'/api/predictions/predictions/student/{student_a.id}/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Tests : register_view — absence du token de vérification
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRegisterViewTokenLeak:
    """Vérifie que le token de vérification n'est plus exposé dans la réponse d'inscription."""

    def test_verification_token_not_in_response(self):
        """Le token de vérification ne doit PAS apparaître dans la réponse d'inscription."""
        client = APIClient()
        _pw = 'T3stP@ssW!rd'  # pragma: allowlist secret  # noqa: S105
        data = {
            'email': 'nouveau@test.ca',
            'password': _pw,
            'password_confirm': _pw,
            'first_name': 'Nouveau',
            'last_name': 'Utilisateur',
            'role': 'teacher',
        }
        resp = client.post('/api/auth/register/', data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'verification_token' not in resp.data

    def test_register_returns_user_data(self):
        """La réponse d'inscription contient bien les données de l'utilisateur."""
        client = APIClient()
        _pw = 'T3stP@ssW!rd'  # pragma: allowlist secret  # noqa: S105
        data = {
            'email': 'test2@test.ca',
            'password': _pw,
            'password_confirm': _pw,
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'teacher',
        }
        resp = client.post('/api/auth/register/', data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'user' in resp.data
        assert 'message' in resp.data


# ---------------------------------------------------------------------------
# Tests : Contrôle d'accès général sur les alertes (création/suppression)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAlertWritePermissions:
    """Vérifie les permissions d'écriture sur les alertes."""

    def test_unauthenticated_cannot_create_alert(self, student_a):
        """Un utilisateur non authentifié ne peut pas créer d'alerte."""
        client = APIClient()
        resp = client.post('/api/alerts/alerts/', {
            'student': str(student_a.id),
            'type': 'performance',
            'level': 'low',
            'message': 'Test'
        }, format='json')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_teacher_cannot_delete_alert(self, teacher, alert_a):
        """Un enseignant sans accès à l'étudiant ne peut pas supprimer l'alerte."""
        client = auth_client(teacher)
        resp = client.delete(f'/api/alerts/alerts/{alert_a.id}/')
        # 403 (pas accès) ou 404 (filtré du queryset) — les deux sont acceptables
        assert resp.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )

    def test_admin_can_delete_alert(self, admin, alert_a):
        """Un admin peut supprimer une alerte."""
        client = auth_client(admin)
        resp = client.delete(f'/api/alerts/alerts/{alert_a.id}/')
        assert resp.status_code == status.HTTP_204_NO_CONTENT
