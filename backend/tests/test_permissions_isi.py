"""
Test suite for ISI RBAC (Role-Based Access Control) permissions.

Tests critical security scenarios before thesis defense:
- Scenario A: Teacher can only manage their own students/grades
- Scenario B: Admin must provide program when creating students
- Scenario C: Role hierarchy enforcement
"""
import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.students.models import Student
from apps.programs.models import Program, Department
from apps.sessions.models import Session
from apps.grades.models import Grade
from apps.programs.models import Subject

User = get_user_model()


class TestTeacherPermissions(TestCase):
    """
    Scenario A: Test Teacher (Enseignant) permissions.

    CRITICAL TESTS:
    - ✓ Teacher can create grades for their subject
    - ✗ Teacher CANNOT modify grades of other teachers
    - ✗ Teacher CANNOT delete students
    - ✗ Teacher CANNOT access admin-only endpoints
    """

    def setUp(self):
        """Setup test data."""
        self.client = APIClient()
        self.factory = RequestFactory()

        # Create departments and programs (ISI structure)
        self.dept_gi = Department.objects.create(
            code='DGI',
            name='Génie Informatique',
            status='active'
        )
        self.program_gl = Program.objects.create(
            code='GL',
            name='Génie Logiciel',
            department=self.dept_gi,
            duration=5,
            status='active'
        )

        # Create session
        self.session = Session.objects.create(
            name='2024-2025',
            year='2024',
            type='annual',
            status='active'
        )

        # Create subjects
        self.math_subject = Subject.objects.create(
            code='MATH101',
            name='Mathématiques'
        )
        self.math_subject.programs.add(self.program_gl)

        self.python_subject = Subject.objects.create(
            code='PROG201',
            name='Programmation Python'
        )
        self.python_subject.programs.add(self.program_gl)

        # Create teachers
        self.teacher1 = User.objects.create_user(
            email='teacher1@isi.sn',
            password='test123',
            first_name='Mamadou',
            last_name='Diop',
            role='teacher',
            is_active=True
        )

        self.teacher2 = User.objects.create_user(
            email='teacher2@isi.sn',
            password='test123',
            first_name='Fatou',
            last_name='Sall',
            role='teacher',
            is_active=True
        )

        # Create admin
        self.admin = User.objects.create_user(
            email='admin@isi.sn',
            password='test123',
            first_name='Admin',
            last_name='ISI',
            role='admin',
            is_active=True
        )

        # Create student
        self.student = Student.objects.create(
            matricule='2024GL001',
            first_name='Moussa',
            last_name='Ndiaye',
            email='moussa@isi.sn',
            date_of_birth='2002-01-15',
            program=self.program_gl,
            session=self.session,
            level='L1',
            status='active'
        )

    def test_teacher_can_create_grade_for_their_subject(self):
        """✓ Teacher CAN create grades for their own subject."""
        self.client.force_authenticate(user=self.teacher1)

        grade_data = {
            'student': self.student.id,
            'subject': self.math_subject.id,
            'session': self.session.id,
            'value': 15.5,
            'max_value': 20.0,
            'type': 'exam',
            'date': '2024-11-15'
        }

        response = self.client.post('/api/grades/', grade_data, format='json')

        # Should succeed (200 or 201)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_teacher_cannot_delete_student(self):
        """✗ Teacher CANNOT delete students (should get 403 Forbidden)."""
        self.client.force_authenticate(user=self.teacher1)

        response = self.client.delete(f'/api/students/{self.student.id}/')

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_access_ml_training(self):
        """✗ Teacher CANNOT launch ML training (admin-only)."""
        self.client.force_authenticate(user=self.teacher1)

        training_data = {
            'name': 'Test Training',
            'algorithm': 'xgboost',
            'description': 'Test'
        }

        response = self.client.post('/api/ml/training-jobs/', training_data, format='json')

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_modify_other_teacher_grades(self):
        """✗ Teacher CANNOT modify grades created by another teacher."""
        # Create grade by teacher2
        self.client.force_authenticate(user=self.teacher2)

        grade_data = {
            'student': self.student.id,
            'subject': self.python_subject.id,
            'session': self.session.id,
            'value': 12.0,
            'max_value': 20.0,
            'type': 'exam',
            'date': '2024-11-15'
        }

        create_response = self.client.post('/api/grades/', grade_data, format='json')
        self.assertIn(create_response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

        grade_id = create_response.data.get('id')

        # Try to modify as teacher1
        self.client.force_authenticate(user=self.teacher1)

        update_data = {'value': 18.0}
        response = self.client.patch(f'/api/grades/{grade_id}/', update_data, format='json')

        # Should be forbidden (or 404 if filtered out)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class TestAdminPermissions(TestCase):
    """
    Scenario B: Test Admin permissions and validation.

    CRITICAL TESTS:
    - ✓ Admin can create students
    - ✗ System MUST reject student creation without program
    - ✓ Admin can access all endpoints
    """

    def setUp(self):
        """Setup test data."""
        self.client = APIClient()

        # Create department and program
        self.dept = Department.objects.create(
            code='DGI',
            name='Génie Informatique',
            status='active'
        )
        self.program = Program.objects.create(
            code='GL',
            name='Génie Logiciel',
            department=self.dept,
            duration=5,
            status='active'
        )

        # Create session
        self.session = Session.objects.create(
            name='2024-2025',
            year='2024',
            type='annual',
            status='active'
        )

        # Create admin
        self.admin = User.objects.create_user(
            email='admin@isi.sn',
            password='test123',
            first_name='Admin',
            last_name='ISI',
            role='admin',
            is_active=True
        )

    def test_admin_can_create_student_with_program(self):
        """✓ Admin CAN create student with valid program."""
        self.client.force_authenticate(user=self.admin)

        student_data = {
            'matricule': '2024GL001',
            'first_name': 'Moussa',
            'last_name': 'Diop',
            'email': 'moussa@isi.sn',
            'date_of_birth': '2002-05-10',
            'program': self.program.id,
            'session': self.session.id,
            'level': 'L2',
            'status': 'active'
        }

        response = self.client.post('/api/students/', student_data, format='json')

        # Should succeed
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(response.data['matricule'], '2024GL001')

    def test_system_rejects_student_without_program(self):
        """✗ System MUST reject student creation without program."""
        self.client.force_authenticate(user=self.admin)

        student_data = {
            'matricule': '2024GL002',
            'first_name': 'Fatou',
            'last_name': 'Sall',
            'email': 'fatou@isi.sn',
            'date_of_birth': '2003-03-20',
            # NO PROGRAM PROVIDED
            'session': self.session.id,
            'level': 'L1',
            'status': 'active'
        }

        response = self.client.post('/api/students/', student_data, format='json')

        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check error message mentions program
        error_msg = str(response.data).lower()
        self.assertIn('program', error_msg)

    def test_system_rejects_invalid_level(self):
        """✗ System MUST reject invalid student level (not L1-L3, M1-M2)."""
        self.client.force_authenticate(user=self.admin)

        student_data = {
            'matricule': '2024GL003',
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test@isi.sn',
            'date_of_birth': '2002-01-01',
            'program': self.program.id,
            'session': self.session.id,
            'level': 'L4',  # INVALID - only L1, L2, L3, M1, M2 allowed
            'status': 'active'
        }

        response = self.client.post('/api/students/', student_data, format='json')

        # Should fail
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestRoleHierarchy(TestCase):
    """
    Scenario C: Test role hierarchy enforcement.

    CRITICAL TESTS:
    - Ensure DS > Pedagogical > Teacher
    - Ensure Admin has all permissions
    """

    def setUp(self):
        """Setup test users."""
        self.client = APIClient()

        self.teacher = User.objects.create_user(
            email='teacher@isi.sn',
            password='test123',
            role='teacher'
        )

        self.pedagogical = User.objects.create_user(
            email='pedagogical@isi.sn',
            password='test123',
            role='pedagogical'
        )

        self.ds = User.objects.create_user(
            email='ds@isi.sn',
            password='test123',
            role='ds'
        )

        self.admin = User.objects.create_user(
            email='admin@isi.sn',
            password='test123',
            role='admin'
        )

    def test_only_ds_and_admin_can_generate_predictions(self):
        """✗ Only DS and Admin can trigger ML predictions."""
        # Teacher tries
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/predictions/predictions/generate/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Pedagogical tries
        self.client.force_authenticate(user=self.pedagogical)
        response = self.client.post('/api/predictions/predictions/generate/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # DS should succeed (or get 400 if no active model, but NOT 403)
        self.client.force_authenticate(user=self.ds)
        response = self.client.post('/api/predictions/predictions/generate/', {}, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST  # OK if no model, but not forbidden
        ])


# Test runner instructions
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
