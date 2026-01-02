"""
Tests for Student app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date
from .models import Student
from apps.programs.models import Program

User = get_user_model()


class StudentModelTest(TestCase):
    """Tests for Student model."""

    def setUp(self):
        """Set up test data."""
        self.program = Program.objects.create(
            code='TEST-001',
            name='Test Program',
            duration_months=24,
            credits_required=60
        )

    def test_create_student(self):
        """Test creating a student."""
        student = Student.objects.create(
            student_id='TEST001',
            first_name='Test',
            last_name='Student',
            email='test.student@test.ca',
            program=self.program,
            admission_date=date.today(),
            status=Student.Status.ACTIVE
        )

        self.assertEqual(student.student_id, 'TEST001')
        self.assertEqual(student.get_full_name(), 'Test Student')
        self.assertEqual(student.status, Student.Status.ACTIVE)

    def test_student_str(self):
        """Test student string representation."""
        student = Student.objects.create(
            student_id='TEST002',
            first_name='John',
            last_name='Doe',
            email='john.doe@test.ca',
            program=self.program,
            admission_date=date.today()
        )

        expected_str = 'TEST002 - John Doe'
        self.assertEqual(str(student), expected_str)


class StudentAPITest(APITestCase):
    """Tests for Student API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create program
        self.program = Program.objects.create(
            code='TEST-001',
            name='Test Program',
            duration_months=24,
            credits_required=60
        )

        # Create user
        self.user = User.objects.create_user(
            email='admin@test.ca',
            password='testpass123',
            role=User.Role.ADMIN
        )

        # Create client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test student
        self.student = Student.objects.create(
            student_id='TEST001',
            first_name='Test',
            last_name='Student',
            email='test.student@test.ca',
            program=self.program,
            admission_date=date.today(),
            status=Student.Status.ACTIVE
        )

    def test_list_students(self):
        """Test listing students."""
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_get_student_detail(self):
        """Test getting student details."""
        response = self.client.get(f'/api/students/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], 'TEST001')
        self.assertEqual(response.data['full_name'], 'Test Student')

    def test_create_student(self):
        """Test creating a new student."""
        data = {
            'student_id': 'TEST002',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'new.student@test.ca',
            'program': self.program.id,
            'admission_date': date.today().isoformat(),
        }

        response = self.client.post('/api/students/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 2)

        # Verify created student
        new_student = Student.objects.get(student_id='TEST002')
        self.assertEqual(new_student.first_name, 'New')
        self.assertEqual(new_student.last_name, 'Student')

    def test_update_student(self):
        """Test updating a student."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '514-123-4567'
        }

        response = self.client.patch(f'/api/students/{self.student.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Updated')
        self.assertEqual(self.student.last_name, 'Name')

    def test_change_student_status(self):
        """Test changing student status."""
        data = {'status': Student.Status.DROPPED}

        response = self.client.post(
            f'/api/students/{self.student.id}/change_status/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, Student.Status.DROPPED)

    def test_filter_students_by_status(self):
        """Test filtering students by status."""
        # Create another student with different status
        Student.objects.create(
            student_id='TEST003',
            first_name='Inactive',
            last_name='Student',
            email='inactive@test.ca',
            program=self.program,
            admission_date=date.today(),
            status=Student.Status.INACTIVE
        )

        # Filter by active status
        response = self.client.get('/api/students/?status=ACTIVE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only return active students
        for student in response.data['results']:
            self.assertEqual(student['status'], Student.Status.ACTIVE)

    def test_search_students(self):
        """Test searching students."""
        response = self.client.get('/api/students/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_unauthorized_access(self):
        """Test that unauthenticated requests are rejected."""
        # Create unauthenticated client
        client = APIClient()
        response = client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_student(self):
        """Test deleting a student."""
        student_id = self.student.id
        response = self.client.delete(f'/api/students/{student_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify student is deleted
        self.assertFalse(Student.objects.filter(id=student_id).exists())
