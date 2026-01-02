"""
Script pour créer des données de test dans la base de données SPAS.
Usage: python manage.py shell < scripts/create_sample_data.py
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.students.models import Student
from apps.programs.models import Program, Course
from apps.sessions.models import AcademicPeriod, CourseSession, Enrollment
from apps.grades.models import Grade, CourseGradeSummary
from apps.attendance.models import AttendanceRecord, AttendanceSummary
from apps.ml.models import MLModel

User = get_user_model()


def create_sample_data():
    """Create sample data for testing."""
    print("Creating sample data for SPAS...")

    # 1. Create Users
    print("\n1. Creating users...")
    admin, created = User.objects.get_or_create(
        email='admin@spas.ca',
        defaults={
            'first_name': 'Admin',
            'last_name': 'System',
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"  ✓ Admin user created: {admin.email}")

    teacher1, created = User.objects.get_or_create(
        email='jean.dupont@spas.ca',
        defaults={
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'role': User.Role.TEACHER,
            'department': 'Informatique'
        }
    )
    if created:
        teacher1.set_password('teacher123')
        teacher1.save()
        print(f"  ✓ Teacher created: {teacher1.email}")

    advisor1, created = User.objects.get_or_create(
        email='marie.martin@spas.ca',
        defaults={
            'first_name': 'Marie',
            'last_name': 'Martin',
            'role': User.Role.ADVISOR,
            'department': 'Services aux étudiants'
        }
    )
    if created:
        advisor1.set_password('advisor123')
        advisor1.save()
        print(f"  ✓ Advisor created: {advisor1.email}")

    # 2. Create Programs
    print("\n2. Creating programs...")
    program_ti, created = Program.objects.get_or_create(
        code='420.B0',
        defaults={
            'name': 'Techniques de l\'informatique',
            'description': 'Programme collégial en informatique',
            'duration_months': 36,
            'credits_required': 90
        }
    )
    if created:
        print(f"  ✓ Program created: {program_ti.code}")

    # 3. Create Courses
    print("\n3. Creating courses...")
    courses_data = [
        {'code': '420-101', 'name': 'Introduction à la programmation', 'credits': 3},
        {'code': '420-201', 'name': 'Programmation orientée objet', 'credits': 3},
        {'code': '420-301', 'name': 'Bases de données', 'credits': 3},
        {'code': '420-401', 'name': 'Développement web', 'credits': 3},
        {'code': '420-501', 'name': 'Réseaux informatiques', 'credits': 3},
    ]

    courses = []
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            code=course_data['code'],
            defaults={
                'name': course_data['name'],
                'credits': course_data['credits'],
                'program': program_ti
            }
        )
        courses.append(course)
        if created:
            print(f"  ✓ Course created: {course.code}")

    # 4. Create Academic Period
    print("\n4. Creating academic periods...")
    period, created = AcademicPeriod.objects.get_or_create(
        name='Automne 2024',
        defaults={
            'season': AcademicPeriod.Season.FALL,
            'year': 2024,
            'start_date': date(2024, 9, 1),
            'end_date': date(2024, 12, 20),
            'is_active': True
        }
    )
    if created:
        print(f"  ✓ Academic period created: {period.name}")

    # 5. Create Course Sessions
    print("\n5. Creating course sessions...")
    sessions = []
    for course in courses:
        session, created = CourseSession.objects.get_or_create(
            course=course,
            academic_period=period,
            section='01',
            defaults={
                'teacher': teacher1,
                'max_students': 30,
                'room': 'A-101'
            }
        )
        sessions.append(session)
        if created:
            print(f"  ✓ Session created: {session}")

    # 6. Create Students
    print("\n6. Creating students...")
    students_data = [
        {'id': '2024001', 'first': 'Alexandre', 'last': 'Tremblay', 'email': 'alexandre.tremblay@student.spas.ca'},
        {'id': '2024002', 'first': 'Sophie', 'last': 'Gagnon', 'email': 'sophie.gagnon@student.spas.ca'},
        {'id': '2024003', 'first': 'François', 'last': 'Roy', 'email': 'francois.roy@student.spas.ca'},
        {'id': '2024004', 'first': 'Amélie', 'last': 'Côté', 'email': 'amelie.cote@student.spas.ca'},
        {'id': '2024005', 'first': 'Gabriel', 'last': 'Bouchard', 'email': 'gabriel.bouchard@student.spas.ca'},
        {'id': '2024006', 'first': 'Émilie', 'last': 'Lavoie', 'email': 'emilie.lavoie@student.spas.ca'},
        {'id': '2024007', 'first': 'Maxime', 'last': 'Bergeron', 'email': 'maxime.bergeron@student.spas.ca'},
        {'id': '2024008', 'first': 'Catherine', 'last': 'Paquette', 'email': 'catherine.paquette@student.spas.ca'},
    ]

    students = []
    for student_data in students_data:
        student, created = Student.objects.get_or_create(
            student_id=student_data['id'],
            defaults={
                'first_name': student_data['first'],
                'last_name': student_data['last'],
                'email': student_data['email'],
                'program': program_ti,
                'admission_date': date(2024, 8, 15),
                'status': Student.Status.ACTIVE
            }
        )
        students.append(student)
        if created:
            print(f"  ✓ Student created: {student.student_id}")

    # 7. Create Enrollments
    print("\n7. Creating enrollments...")
    for student in students:
        for session in sessions[:3]:  # Enroll in first 3 courses
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course_session=session,
                defaults={
                    'status': Enrollment.Status.ENROLLED
                }
            )
            if created:
                print(f"  ✓ Enrollment: {student.student_id} -> {session.course.code}")

    # 8. Create Sample Grades
    print("\n8. Creating sample grades...")
    grade_values = [85, 78, 92, 65, 88]  # Various grades
    for i, student in enumerate(students[:5]):
        for enrollment in student.enrollments.all():
            # Create 3 evaluations per course
            for j, eval_name in enumerate(['Examen 1', 'TP', 'Examen Final']):
                grade_value = grade_values[i] + (j * 5 - 5)  # Vary grades
                Grade.objects.get_or_create(
                    enrollment=enrollment,
                    evaluation_name=eval_name,
                    defaults={
                        'grade': Decimal(str(grade_value)),
                        'weight': Decimal('33.33'),
                        'evaluation_date': date.today() - timedelta(days=30-j*10)
                    }
                )

            # Calculate summary
            summary, _ = CourseGradeSummary.objects.get_or_create(enrollment=enrollment)
            summary.calculate_final_grade()
            print(f"  ✓ Grades for {student.student_id} in {enrollment.course_session.course.code}")

    # 9. Create Sample Attendance
    print("\n9. Creating sample attendance...")
    for student in students[:5]:
        for enrollment in student.enrollments.all():
            # Create 10 attendance records
            for i in range(10):
                # Vary attendance: some students have more absences
                if student == students[0]:  # Good student
                    status = AttendanceRecord.Status.PRESENT
                elif student == students[1]:  # Some absences
                    status = AttendanceRecord.Status.ABSENT if i % 3 == 0 else AttendanceRecord.Status.PRESENT
                else:
                    status = AttendanceRecord.Status.PRESENT if i % 2 == 0 else AttendanceRecord.Status.ABSENT

                AttendanceRecord.objects.get_or_create(
                    enrollment=enrollment,
                    date=date.today() - timedelta(days=50-i*5),
                    defaults={'status': status}
                )

            # Calculate summary
            summary, _ = AttendanceSummary.objects.get_or_create(enrollment=enrollment)
            summary.calculate_summary()
            print(f"  ✓ Attendance for {student.student_id} in {enrollment.course_session.course.code}")

    # 10. Create ML Model
    print("\n10. Creating ML model...")
    ml_model, created = MLModel.objects.get_or_create(
        name='Dropout Predictor v1',
        defaults={
            'version': '1.0.0',
            'model_type': MLModel.ModelType.DROPOUT_PREDICTION,
            'description': 'Random Forest model for predicting student dropout',
            'file_path': 'ml_models/dropout_v1.pkl',
            'accuracy': Decimal('85.5'),
            'is_active': True
        }
    )
    if created:
        print(f"  ✓ ML Model created: {ml_model.name}")

    print("\n" + "="*50)
    print("Sample data creation completed!")
    print("="*50)
    print("\nLogin credentials:")
    print("  Admin: admin@spas.ca / admin123")
    print("  Teacher: jean.dupont@spas.ca / teacher123")
    print("  Advisor: marie.martin@spas.ca / advisor123")
    print("\nYou can now:")
    print("  1. Access admin panel: http://localhost:8000/admin/")
    print("  2. Access API docs: http://localhost:8000/api/docs/")
    print("  3. Get JWT token: POST http://localhost:8000/api/auth/token/")


if __name__ == '__main__':
    create_sample_data()
