"""
Pytest configuration and fixtures for SPAS API tests.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""
    def _create_user(
        email='test@spas.ca',
        password='testpassword123',
        first_name='Test',
        last_name='User',
        role='teacher',
        is_active=True,
        **kwargs
    ):
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=is_active,
            **kwargs
        )
        return user
    return _create_user


@pytest.fixture
def admin_user(create_user):
    """Create an admin user."""
    return create_user(
        email='admin@spas.ca',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def teacher_user(create_user):
    """Create a teacher user."""
    return create_user(
        email='teacher@spas.ca',
        password='teacher123',
        first_name='Jean',
        last_name='Dupont',
        role='teacher'
    )


@pytest.fixture
def ds_user(create_user):
    """Create a data scientist user."""
    return create_user(
        email='ds@spas.ca',
        password='ds123456',
        first_name='Marie',
        last_name='Martin',
        role='ds'
    )


@pytest.fixture
def pedagogical_user(create_user):
    """Create a pedagogical advisor user."""
    return create_user(
        email='pedagogical@spas.ca',
        password='pedagogical123',
        first_name='Pierre',
        last_name='Tremblay',
        role='pedagogical'
    )


@pytest.fixture
def authenticated_client(api_client, teacher_user):
    """Return an authenticated API client with teacher role."""
    refresh = RefreshToken.for_user(teacher_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_authenticated_client(api_client, admin_user):
    """Return an authenticated API client with admin role."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def program(db):
    """Create a test program."""
    from apps.programs.models import Program
    return Program.objects.create(
        name='Techniques de l\'informatique',
        code='420.B0',
        description='Programme collégial en informatique',
        duration=3,
        status='active'
    )


@pytest.fixture
def session(db):
    """Create a test session."""
    from apps.sessions.models import Session
    from datetime import date
    return Session.objects.create(
        name='Automne 2024',
        year='2024-2025',
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 20),
        status='active'
    )


@pytest.fixture
def student(db, program, session):
    """Create a test student."""
    from apps.students.models import Student
    from datetime import date
    return Student.objects.create(
        matricule='2024001',
        first_name='Alexandre',
        last_name='Tremblay',
        email='alexandre.tremblay@student.spas.ca',
        phone='+1 514 555-0001',
        date_of_birth=date(2000, 1, 15),
        program=program,
        session=session,
        status='active',
        risk_level='low',
        risk_score=15
    )


@pytest.fixture
def high_risk_student(db, program, session):
    """Create a high-risk test student."""
    from apps.students.models import Student
    from datetime import date
    return Student.objects.create(
        matricule='2024002',
        first_name='Sophie',
        last_name='Gagnon',
        email='sophie.gagnon@student.spas.ca',
        date_of_birth=date(2001, 5, 20),
        program=program,
        session=session,
        status='active',
        risk_level='high',
        risk_score=85
    )


@pytest.fixture
def subject(db, program):
    """Create a test subject."""
    from apps.programs.models import Subject
    subject = Subject.objects.create(
        name='Introduction à la programmation',
        code='420-101',
        description='Cours d\'introduction'
    )
    subject.programs.add(program)
    return subject


@pytest.fixture
def alert(db, student):
    """Create a test alert."""
    from apps.alerts.models import Alert
    return Alert.objects.create(
        student=student,
        type='performance',
        level='medium',
        message='Alerte de performance pour cet étudiant',
        status='new'
    )
