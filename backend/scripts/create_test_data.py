#!/usr/bin/env python
"""
Script to create test data for SPAS.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from datetime import date
from apps.students.models import Student
from apps.programs.models import Program
from apps.sessions.models import Session
from apps.grades.models import Grade
from apps.attendance.models import Attendance


def create_test_data():
    """Create test data for SPAS."""
    print("=== Creating Test Data ===\n")

    # Create test program
    program, created = Program.objects.get_or_create(
        code='INFO',
        defaults={'name': 'Informatique', 'duration': 3}
    )
    print(f"Program: {program.name} {'(created)' if created else '(exists)'}")

    # Create test session
    session, created = Session.objects.get_or_create(
        name='2024-2025',
        defaults={
            'year': '2024',
            'start_date': date(2024, 9, 1),
            'end_date': date(2025, 6, 30),
            'status': 'active'
        }
    )
    print(f"Session: {session.name} {'(created)' if created else '(exists)'}")

    # Create test students
    students_data = [
        {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean@test.com',
            'matricule': 'ETU001',
            'date_of_birth': date(2000, 5, 15)
        },
        {
            'first_name': 'Marie',
            'last_name': 'Martin',
            'email': 'marie@test.com',
            'matricule': 'ETU002',
            'date_of_birth': date(2001, 3, 20)
        },
        {
            'first_name': 'Pierre',
            'last_name': 'Bernard',
            'email': 'pierre@test.com',
            'matricule': 'ETU003',
            'date_of_birth': date(1999, 11, 8)
        },
    ]

    students = []
    for data in students_data:
        student, created = Student.objects.get_or_create(
            matricule=data['matricule'],
            defaults={**data, 'program': program, 'session': session, 'status': 'active'}
        )
        students.append(student)
        status = 'created' if created else 'exists'
        print(f"Student: {student.first_name} {student.last_name} ({status})")

    print(f"\nTotal students: {Student.objects.count()}")
    print("\n=== Test Data Creation Complete ===")
    
    return students


if __name__ == '__main__':
    create_test_data()
