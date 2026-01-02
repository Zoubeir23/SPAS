"""
Django management command to initialize SPAS with sample data.
Usage: python manage.py init_spas
       python manage.py init_spas --clear
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.students.models import Student
from apps.programs.models import Program, Subject
from apps.sessions.models import Session
from apps.grades.models import Grade
from apps.attendance.models import Attendance
from apps.ml.models import MLModel
from apps.alerts.models import Alert
from datetime import date, timedelta
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize SPAS database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            # Clear data in reverse order of dependencies
            Alert.objects.all().delete()
            Attendance.objects.all().delete()
            Grade.objects.all().delete()
            Student.objects.all().delete()
            Subject.objects.all().delete()
            Program.objects.all().delete()
            Session.objects.all().delete()
            MLModel.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        self.stdout.write(self.style.SUCCESS('Creating sample data for SPAS...'))

        # 1. Create Users
        self.stdout.write('Creating users...')
        admin, created = User.objects.get_or_create(
            email='admin@isi.edu',
            defaults={
                'first_name': 'Admin',
                'last_name': 'System',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('password123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Admin: {admin.email}'))
        else:
            self.stdout.write(f'  - Admin already exists: {admin.email}')

        teacher, created = User.objects.get_or_create(
            email='teacher@isi.edu',
            defaults={
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'role': User.Role.TEACHER,
            }
        )
        if created:
            teacher.set_password('password123')
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Teacher: {teacher.email}'))

        ds_user, created = User.objects.get_or_create(
            email='ds@isi.edu',
            defaults={
                'first_name': 'Marie',
                'last_name': 'Sarr',
                'role': User.Role.DS,
            }
        )
        if created:
            ds_user.set_password('password123')
            ds_user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Data Scientist: {ds_user.email}'))

        pedagogical, created = User.objects.get_or_create(
            email='pedagogical@isi.edu',
            defaults={
                'first_name': 'Fatou',
                'last_name': 'Diallo',
                'role': User.Role.PEDAGOGICAL,
            }
        )
        if created:
            pedagogical.set_password('password123')
            pedagogical.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Pedagogical: {pedagogical.email}'))

        # 2. Create Programs
        self.stdout.write('Creating programs...')
        programs_data = [
            {'code': 'L-INFO', 'name': 'Licence Informatique', 'duration': 3},
            {'code': 'M-DS', 'name': 'Master Data Science', 'duration': 2},
            {'code': 'L-RES', 'name': 'Licence Réseaux', 'duration': 3},
        ]

        programs = []
        for prog_data in programs_data:
            program, created = Program.objects.get_or_create(
                code=prog_data['code'],
                defaults={
                    'name': prog_data['name'],
                    'duration': prog_data['duration'],
                    'status': 'active'
                }
            )
            programs.append(program)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {program.name}'))

        # 3. Create Subjects
        self.stdout.write('Creating subjects...')
        subjects_data = [
            {'code': 'MATH101', 'name': 'Mathématiques'},
            {'code': 'ALGO101', 'name': 'Algorithmique'},
            {'code': 'PROG101', 'name': 'Programmation'},
            {'code': 'DB101', 'name': 'Bases de Données'},
            {'code': 'NET101', 'name': 'Réseaux'},
            {'code': 'ENG101', 'name': 'Anglais'},
        ]

        subjects = []
        for subj_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subj_data['code'],
                defaults={'name': subj_data['name']}
            )
            subjects.append(subject)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {subject.name}'))

        # 4. Create Session
        self.stdout.write('Creating academic session...')
        session, created = Session.objects.get_or_create(
            name='2025-2026',
            defaults={
                'year': '2025',
                'start_date': date(2025, 10, 1),
                'end_date': date(2026, 6, 30),
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Session: {session.name}'))

        # 5. Create Students
        self.stdout.write('Creating students...')
        students_data = [
            # Good students (low risk)
            {'first': 'Amadou', 'last': 'Diallo', 'profile': 'good'},
            {'first': 'Fatou', 'last': 'Ndiaye', 'profile': 'good'},
            {'first': 'Moussa', 'last': 'Fall', 'profile': 'good'},
            {'first': 'Aminata', 'last': 'Sow', 'profile': 'good'},
            {'first': 'Ibrahima', 'last': 'Ba', 'profile': 'good'},
            # At-risk students (medium risk)
            {'first': 'Ousmane', 'last': 'Diop', 'profile': 'at_risk'},
            {'first': 'Awa', 'last': 'Sy', 'profile': 'at_risk'},
            {'first': 'Cheikh', 'last': 'Gueye', 'profile': 'at_risk'},
            # High-risk students
            {'first': 'Modou', 'last': 'Sarr', 'profile': 'high_risk'},
            {'first': 'Khady', 'last': 'Kane', 'profile': 'high_risk'},
        ]

        students = []
        for i, student_data in enumerate(students_data):
            matricule = f'ISI2025{i+1:04d}'
            email = f"{student_data['first'].lower()}.{student_data['last'].lower()}@student.isi.edu"
            
            # Determine risk level
            if student_data['profile'] == 'good':
                risk_level = 'low'
            elif student_data['profile'] == 'at_risk':
                risk_level = 'medium'
            else:
                risk_level = 'high'
            
            student, created = Student.objects.get_or_create(
                matricule=matricule,
                defaults={
                    'first_name': student_data['first'],
                    'last_name': student_data['last'],
                    'email': email,
                    'date_of_birth': date(2000, 1, 1) + timedelta(days=i*30),
                    'program': random.choice(programs),
                    'session': session,
                    'status': 'active',
                    'risk_level': risk_level,
                }
            )
            students.append((student, student_data['profile']))
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {student.get_full_name()} ({risk_level})'))

        # 6. Create Grades
        self.stdout.write('Creating grades...')
        grades_count = 0
        for student, profile in students:
            # Grade parameters based on profile
            if profile == 'good':
                mean, std = 15.0, 2.0
            elif profile == 'at_risk':
                mean, std = 10.0, 3.0
            else:
                mean, std = 7.0, 3.0
            
            for subject in subjects[:4]:  # 4 subjects per student
                for eval_type in ['exam', 'assignment']:
                    value = max(0, min(20, random.gauss(mean, std)))
                    grade, created = Grade.objects.get_or_create(
                        student=student,
                        subject=subject,
                        session=session,
                        type=eval_type,
                        defaults={
                            'value': round(Decimal(str(value)), 1),
                            'max_value': Decimal('20'),
                            'date': date.today() - timedelta(days=random.randint(1, 60))
                        }
                    )
                    if created:
                        grades_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {grades_count} grades created'))

        # 7. Create Attendance
        self.stdout.write('Creating attendance records...')
        attendance_count = 0
        for student, profile in students:
            # Attendance parameters based on profile
            if profile == 'good':
                present_rate = 0.95
            elif profile == 'at_risk':
                present_rate = 0.75
            else:
                present_rate = 0.55
            
            for day_offset in range(30):  # 30 days of attendance
                subject = random.choice(subjects)
                status = 'present' if random.random() < present_rate else 'absent'
                
                att, created = Attendance.objects.get_or_create(
                    student=student,
                    subject=subject,
                    date=date.today() - timedelta(days=day_offset),
                    defaults={'status': status}
                )
                if created:
                    attendance_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {attendance_count} attendance records created'))

        # 8. Create Alerts for high-risk students
        self.stdout.write('Creating alerts...')
        alerts_count = 0
        for student, profile in students:
            if profile in ['at_risk', 'high_risk']:
                level = 'high' if profile == 'high_risk' else 'medium'
                alert, created = Alert.objects.get_or_create(
                    student=student,
                    type='risk',
                    status='new',
                    defaults={
                        'level': level,
                        'message': f'Étudiant à risque: {student.get_full_name()} nécessite une attention particulière.'
                    }
                )
                if created:
                    alerts_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {alerts_count} alerts created'))

        # 9. Create ML Model record
        self.stdout.write('Creating ML model record...')
        ml_model, created = MLModel.objects.get_or_create(
            name='DropoutRiskPredictor',
            version='1.0.0',
            defaults={
                'description': 'Random Forest model for predicting student dropout risk',
                'accuracy': Decimal('85.5'),
                'precision': Decimal('84.0'),
                'recall': Decimal('86.0'),
                'f1_score': Decimal('85.0'),
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ ML Model: {ml_model.name} v{ml_model.version}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: admin@isi.edu / password123')
        self.stdout.write('  Teacher: teacher@isi.edu / password123')
        self.stdout.write('  Data Scientist: ds@isi.edu / password123')
        self.stdout.write('  Pedagogical: pedagogical@isi.edu / password123')
        self.stdout.write('\nData summary:')
        self.stdout.write(f'  - Users: {User.objects.count()}')
        self.stdout.write(f'  - Programs: {Program.objects.count()}')
        self.stdout.write(f'  - Subjects: {Subject.objects.count()}')
        self.stdout.write(f'  - Sessions: {Session.objects.count()}')
        self.stdout.write(f'  - Students: {Student.objects.count()}')
        self.stdout.write(f'  - Grades: {Grade.objects.count()}')
        self.stdout.write(f'  - Attendance: {Attendance.objects.count()}')
        self.stdout.write(f'  - Alerts: {Alert.objects.count()}')
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Access admin: http://localhost:8000/admin/')
        self.stdout.write('  2. Access API docs: http://localhost:8000/api/docs/')
        self.stdout.write('  3. Login via frontend: http://localhost:5173/')
