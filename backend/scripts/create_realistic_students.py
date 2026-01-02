#!/usr/bin/env python
"""
Script pour créer des données d'étudiants réalistes dans la base de données.

Ce script crée:
- 50 étudiants avec des profils variés (bons, à risque, haut risque)
- Notes réalistes pour chaque étudiant (exams, devoirs)
- Présences réalistes avec patterns variés

Cela permet d'entraîner le modèle ML sur de vraies données de la DB.

Usage:
    python scripts/create_realistic_students.py
    python scripts/create_realistic_students.py --count 100
"""
import os
import sys
import random
import argparse
from datetime import datetime, timedelta

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from apps.students.models import Student
from apps.programs.models import Program, Subject
from apps.sessions.models import Session
from apps.grades.models import Grade
from apps.attendance.models import Attendance


# Prénoms et noms sénégalais réalistes
FIRST_NAMES_MALE = [
    'Amadou', 'Moussa', 'Ibrahima', 'Cheikh', 'Mamadou', 'Omar', 'Aliou', 
    'Modou', 'Ousmane', 'Abdoulaye', 'Pape', 'Serigne', 'Babacar', 'Malick',
    'Demba', 'Lamine', 'Boubacar', 'Samba', 'Youssou', 'El Hadji'
]

FIRST_NAMES_FEMALE = [
    'Fatou', 'Aminata', 'Awa', 'Mariama', 'Ndèye', 'Aissatou', 'Rokhaya',
    'Khady', 'Mame', 'Dieynaba', 'Sokhna', 'Binta', 'Coumba', 'Rama',
    'Astou', 'Ndeye', 'Yacine', 'Seynabou', 'Marième', 'Adja'
]

LAST_NAMES = [
    'Diallo', 'Ndiaye', 'Fall', 'Diop', 'Sow', 'Ba', 'Sy', 'Mbaye', 
    'Gueye', 'Sarr', 'Kane', 'Faye', 'Thiam', 'Diouf', 'Cissé', 
    'Seck', 'Wade', 'Niang', 'Tall', 'Dieng', 'Ndao', 'Lo'
]

SUBJECTS = [
    ('math', 'Mathématiques'),
    ('physics', 'Physique'),
    ('info', 'Informatique'),
    ('algo', 'Algorithmique'),
    ('db', 'Bases de Données'),
    ('networks', 'Réseaux'),
    ('english', 'Anglais'),
    ('french', 'Français'),
    ('stats', 'Statistiques'),
    ('management', 'Gestion de Projet'),
]


def generate_student_data(profile: str, index: int):
    """Génère les données d'un étudiant selon son profil."""
    
    # Choisir genre
    is_male = random.random() > 0.4  # 60% hommes
    
    if is_male:
        first_name = random.choice(FIRST_NAMES_MALE)
    else:
        first_name = random.choice(FIRST_NAMES_FEMALE)
    
    last_name = random.choice(LAST_NAMES)
    
    # Email unique basé sur timestamp
    timestamp = int(datetime.now().timestamp() * 1000) + index
    email = f"{first_name.lower()}.{last_name.lower()}.{timestamp}@isi.edu"
    
    # Matricule unique
    year = 2024 - random.randint(0, 2)
    matricule = f"ISI{year}{timestamp % 100000:05d}"
    
    # Date de naissance (18-25 ans)
    age = random.randint(18, 25)
    dob = datetime.now() - timedelta(days=age * 365 + random.randint(0, 365))
    
    # Téléphone
    phone = f"+221 7{random.randint(0,9)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'matricule': matricule,
        'date_of_birth': dob.date(),
        'phone': phone,
        'profile': profile,
    }


def generate_grades(student, subjects, profile: str, session):
    """Génère des notes réalistes selon le profil."""
    
    grades = []
    
    for subject in subjects:
        # Nombre de notes par matière
        n_exams = random.randint(2, 4)
        n_assignments = random.randint(1, 3)
        
        # Paramètres selon profil
        if profile == 'good':
            exam_mean, exam_std = 14, 2
            assign_mean, assign_std = 15, 2
        elif profile == 'at_risk':
            exam_mean, exam_std = 10, 3
            assign_mean, assign_std = 11, 3
        else:  # high_risk
            exam_mean, exam_std = 7, 3
            assign_mean, assign_std = 8, 4
        
        # Examens
        for i in range(n_exams):
            value = max(0, min(20, random.gauss(exam_mean, exam_std)))
            date = session.start_date + timedelta(days=random.randint(0, 120))
            
            grade = Grade(
                student=student,
                subject=subject,
                session=session,
                value=round(value, 1),
                max_value=20,
                type='exam',
                date=date
            )
            grades.append(grade)
        
        # Devoirs
        for i in range(n_assignments):
            value = max(0, min(20, random.gauss(assign_mean, assign_std)))
            date = session.start_date + timedelta(days=random.randint(0, 100))
            
            grade = Grade(
                student=student,
                subject=subject,
                session=session,
                value=round(value, 1),
                max_value=20,
                type='assignment',
                date=date
            )
            grades.append(grade)
    
    return grades


def generate_attendance(student, subjects, profile: str, session):
    """Génère des présences réalistes selon le profil."""
    
    attendance_records = []
    
    # Nombre de jours de cours (16 semaines, ~80 jours)
    n_days = random.randint(60, 80)
    
    # Taux selon profil
    if profile == 'good':
        present_rate = random.uniform(0.88, 0.98)
        late_rate = random.uniform(0.01, 0.05)
    elif profile == 'at_risk':
        present_rate = random.uniform(0.65, 0.80)
        late_rate = random.uniform(0.05, 0.15)
    else:  # high_risk
        present_rate = random.uniform(0.40, 0.65)
        late_rate = random.uniform(0.10, 0.25)
    
    current_date = session.start_date
    consecutive_absent = 0
    max_consecutive = 0
    
    for _ in range(n_days):
        subject = random.choice(subjects)
        
        # Déterminer le statut
        rand = random.random()
        if rand < present_rate:
            status = 'present'
            consecutive_absent = 0
        elif rand < present_rate + late_rate:
            status = 'late'
            consecutive_absent = 0
        else:
            status = 'absent'
            consecutive_absent += 1
            max_consecutive = max(max_consecutive, consecutive_absent)
            
            # Pour les étudiants à haut risque, parfois des absences consécutives
            if profile == 'high_risk' and random.random() < 0.3:
                # Continue absent streak
                pass
        
        record = Attendance(
            student=student,
            subject=subject,
            date=current_date,
            status=status,
            justification='' if status == 'present' else ('Retard transport' if status == 'late' else '')
        )
        attendance_records.append(record)
        
        # Avancer d'un jour (sauter weekends)
        current_date += timedelta(days=1)
        while current_date.weekday() >= 5:  # Weekend
            current_date += timedelta(days=1)
    
    return attendance_records


def create_realistic_students(count: int = 50, clear_existing: bool = False):
    """Crée des étudiants réalistes avec notes et présences."""
    
    print("=" * 70)
    print("🎓 SPAS - Création de données d'étudiants réalistes")
    print("=" * 70)
    print()
    
    if clear_existing:
        print("🗑️ Suppression des données existantes...")
        Attendance.objects.all().delete()
        Grade.objects.all().delete()
        Student.objects.exclude(email__in=['admin@isi.edu', 'teacher@isi.edu']).delete()
        print("   ✅ Données supprimées")
        print()
    
    # Récupérer ou créer les programmes
    print("📚 Configuration des programmes et sessions...")
    
    programs = list(Program.objects.filter(status='active'))
    if not programs:
        print("   Création des programmes...")
        programs = [
            Program.objects.create(name="Licence Informatique", code="L-INFO", duration=3, status='active'),
            Program.objects.create(name="Master Data Science", code="M-DS", duration=2, status='active'),
            Program.objects.create(name="Licence Réseaux", code="L-RES", duration=3, status='active'),
        ]
    
    # Récupérer la session existante ou en créer une
    session = Session.objects.first()
    if not session:
        print("   Création de la session...")
        session = Session.objects.create(
            name="2025-2026",
            year="2025",
            start_date=datetime(2025, 10, 1).date(),
            end_date=datetime(2026, 6, 30).date(),
            status='active'
        )
    
    print(f"   Session utilisée: {session}")
    
    # Créer les matières si nécessaires
    subjects = []
    for code, name in SUBJECTS:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
            }
        )
        # Ajouter le programme si ManyToMany
        if created:
            subject.programs.add(random.choice(programs))
        subjects.append(subject)
    
    print(f"   ✅ {len(programs)} programmes, {len(subjects)} matières")
    print()
    
    # Distribution des profils (60% bons, 25% à risque, 15% haut risque)
    n_good = int(count * 0.60)
    n_at_risk = int(count * 0.25)
    n_high_risk = count - n_good - n_at_risk
    
    profiles = ['good'] * n_good + ['at_risk'] * n_at_risk + ['high_risk'] * n_high_risk
    random.shuffle(profiles)
    
    print(f"👥 Création de {count} étudiants...")
    print(f"   - Bons étudiants: {n_good}")
    print(f"   - À risque: {n_at_risk}")
    print(f"   - Haut risque: {n_high_risk}")
    print()
    
    students_created = 0
    grades_created = 0
    attendance_created = 0
    
    for i, profile in enumerate(profiles):
        # Générer données de l'étudiant
        data = generate_student_data(profile, i + 100)
        
        # Vérifier si l'email existe déjà
        if Student.objects.filter(email=data['email']).exists():
            continue
        
        # Créer l'étudiant
        program = random.choice(programs)
        
        student = Student.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            matricule=data['matricule'],
            date_of_birth=data['date_of_birth'],
            phone=data['phone'],
            program=program,
            session=session,
            status='active',
            risk_level='low' if profile == 'good' else ('medium' if profile == 'at_risk' else 'high'),
        )
        students_created += 1
        
        # Générer les notes
        grades = generate_grades(student, subjects, profile, session)
        Grade.objects.bulk_create(grades)
        grades_created += len(grades)
        
        # Générer les présences
        attendance = generate_attendance(student, subjects, profile, session)
        Attendance.objects.bulk_create(attendance)
        attendance_created += len(attendance)
        
        # Afficher progression
        if (i + 1) % 10 == 0:
            print(f"   Progression: {i + 1}/{count} étudiants créés")
    
    print()
    print("=" * 70)
    print("✅ CRÉATION TERMINÉE!")
    print("=" * 70)
    print(f"\n📊 Résumé:")
    print(f"   - Étudiants créés: {students_created}")
    print(f"   - Notes créées: {grades_created}")
    print(f"   - Présences créées: {attendance_created}")
    
    # Stats par profil
    print(f"\n📈 Répartition finale:")
    for risk in ['low', 'medium', 'high']:
        count = Student.objects.filter(risk_level=risk, status='active').count()
        print(f"   - {risk}: {count} étudiants")
    
    print()
    print("💡 Prochaine étape:")
    print("   python scripts/train_with_realistic_data.py --source database")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Créer des étudiants réalistes avec notes et présences'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=50,
        help='Nombre d\'étudiants à créer'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Supprimer les données existantes avant création'
    )
    
    args = parser.parse_args()
    
    create_realistic_students(count=args.count, clear_existing=args.clear)
