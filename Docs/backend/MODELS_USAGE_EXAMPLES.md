# Exemples d'Utilisation des Modèles Django - SPAS

Ce document présente des exemples pratiques d'utilisation des modèles Django pour les opérations courantes.

## Table des Matières

1. [Création de Données](#1-création-de-données)
2. [Requêtes de Lecture](#2-requêtes-de-lecture)
3. [Mise à Jour](#3-mise-à-jour)
4. [Analyses et Statistiques](#4-analyses-et-statistiques)
5. [Cas d'Usage ML](#5-cas-dusage-ml)
6. [Gestion des Alertes](#6-gestion-des-alertes)

---

## 1. Création de Données

### Créer un Programme

```python
from apps.programs.models import Program, Subject

# Créer un programme
program = Program.objects.create(
    name="Génie Logiciel",
    code="GL",
    description="Programme de génie logiciel sur 4 ans",
    duration=4,
    status='active'
)

print(f"Programme créé: {program}")  # GL - Génie Logiciel
print(f"Nombre d'étudiants: {program.student_count}")  # 0
```

### Créer des Matières

```python
# Créer des matières
math = Subject.objects.create(
    name="Mathématiques Discrètes",
    code="MAT101",
    description="Introduction aux mathématiques discrètes"
)

algo = Subject.objects.create(
    name="Algorithmes et Structures de Données",
    code="INF201"
)

# Associer les matières au programme
program.subjects.add(math, algo)
```

### Créer une Session

```python
from apps.sessions.models import Session
from datetime import date

session = Session.objects.create(
    name="Automne 2024",
    year="2024-2025",
    start_date=date(2024, 9, 1),
    end_date=date(2024, 12, 20),
    status='active'
)

# Vérifier si la session est active
if session.is_current():
    print("Session actuellement en cours")
```

### Créer un Étudiant

```python
from apps.students.models import Student

student = Student.objects.create(
    matricule="2024001",
    first_name="Jean",
    last_name="Dupont",
    email="jean.dupont@example.com",
    phone="+1234567890",
    date_of_birth=date(2000, 5, 15),
    program=program,
    session=session,
    status='active'
)

print(f"Étudiant créé: {student.get_full_name()}")
print(f"Programme: {student.program_name}")
print(f"Session: {student.session_name}")
```

### Créer des Notes

```python
from apps.grades.models import Grade
from decimal import Decimal

# Créer une note d'examen
grade1 = Grade.objects.create(
    student=student,
    subject=math,
    session=session,
    value=Decimal('85.5'),
    max_value=Decimal('100'),
    type='exam',
    date=date(2024, 10, 15)
)

print(f"Note: {grade1.percentage:.2f}%")  # 85.50%
print(f"Réussite: {grade1.is_passing()}")  # True

# Créer plusieurs notes
grades = [
    Grade(student=student, subject=math, session=session,
          value=90, max_value=100, type='assignment', date=date(2024, 10, 1)),
    Grade(student=student, subject=algo, session=session,
          value=78, max_value=100, type='exam', date=date(2024, 10, 20)),
]
Grade.objects.bulk_create(grades)
```

### Créer des Présences

```python
from apps.attendance.models import Attendance

# Créer une présence
attendance = Attendance.objects.create(
    student=student,
    subject=math,
    date=date(2024, 10, 1),
    status='present'
)

# Créer une absence justifiée
absence = Attendance.objects.create(
    student=student,
    subject=math,
    date=date(2024, 10, 8),
    status='excused',
    justification="Rendez-vous médical"
)

print(f"Présent: {attendance.is_present()}")  # True
print(f"Justifié: {absence.is_justified()}")  # True
```

---

## 2. Requêtes de Lecture

### Récupérer des Étudiants

```python
# Tous les étudiants actifs
active_students = Student.objects.filter(status='active')

# Étudiants d'un programme spécifique
gl_students = Student.objects.filter(
    program__code='GL',
    status='active'
).select_related('program', 'session')

# Étudiants à risque
at_risk_students = Student.objects.filter(
    risk_level__in=['high', 'critical']
).order_by('-risk_score')

# Recherche par nom ou email
search_results = Student.objects.filter(
    models.Q(first_name__icontains='jean') |
    models.Q(last_name__icontains='jean') |
    models.Q(email__icontains='jean')
)
```

### Récupérer des Notes

```python
# Toutes les notes d'un étudiant
student_grades = Grade.objects.filter(
    student=student
).select_related('subject', 'session').order_by('-date')

# Notes d'une matière spécifique
math_grades = Grade.objects.filter(
    student=student,
    subject__code='MAT101'
)

# Notes par type
exam_grades = Grade.objects.filter(
    student=student,
    type='exam'
)

# Notes d'une session
session_grades = Grade.objects.filter(
    student=student,
    session=session
)
```

### Récupérer des Présences

```python
# Toutes les présences d'un étudiant
attendances = Attendance.objects.filter(
    student=student
).select_related('subject').order_by('-date')

# Absences non justifiées
unjustified_absences = Attendance.objects.filter(
    student=student,
    status='absent'
).exclude(justification__isnull=False)

# Présences pour une matière
math_attendance = Attendance.objects.filter(
    student=student,
    subject__code='MAT101'
)
```

---

## 3. Mise à Jour

### Mettre à Jour un Étudiant

```python
# Mise à jour simple
student.phone = "+9876543210"
student.save()

# Mise à jour avec update_fields (plus efficace)
student.email = "new.email@example.com"
student.save(update_fields=['email'])

# Mise à jour du statut
student.status = 'graduated'
student.save()

# Mise à jour de l'évaluation de risque
student.update_risk_assessment(risk_score=75, risk_level='high')
```

### Mettre à Jour en Masse

```python
# Mettre tous les étudiants d'un programme en inactif
Student.objects.filter(
    program__code='OLD_PROGRAM',
    status='active'
).update(status='inactive')

# Mettre à jour les sessions
Session.objects.filter(
    end_date__lt=date.today()
).update(status='completed')
```

---

## 4. Analyses et Statistiques

### Statistiques d'Étudiant

```python
from django.db.models import Avg, Count, Q, F, ExpressionWrapper, FloatField

# Moyenne générale d'un étudiant
avg_grade = Grade.objects.filter(
    student=student
).annotate(
    percentage=ExpressionWrapper(
        F('value') * 100.0 / F('max_value'),
        output_field=FloatField()
    )
).aggregate(average=Avg('percentage'))

print(f"Moyenne générale: {avg_grade['average']:.2f}%")

# Statistiques de présence
attendance_stats = Attendance.objects.filter(
    student=student
).aggregate(
    total=Count('id'),
    present=Count('id', filter=Q(status='present')),
    absent=Count('id', filter=Q(status='absent')),
    late=Count('id', filter=Q(status='late')),
    excused=Count('id', filter=Q(status='excused'))
)

attendance_rate = (attendance_stats['present'] / attendance_stats['total']) * 100
print(f"Taux de présence: {attendance_rate:.2f}%")
```

### Statistiques de Programme

```python
# Nombre d'étudiants par statut dans un programme
program_stats = Student.objects.filter(
    program=program
).values('status').annotate(count=Count('id'))

# Distribution des niveaux de risque
risk_distribution = Student.objects.filter(
    program=program,
    status='active'
).values('risk_level').annotate(count=Count('id'))
```

### Statistiques de Session

```python
# Étudiants par programme dans une session
session_breakdown = Student.objects.filter(
    session=session,
    status='active'
).values(
    'program__name'
).annotate(
    count=Count('id')
).order_by('-count')

# Moyenne générale de la session
session_avg = Grade.objects.filter(
    session=session
).annotate(
    percentage=ExpressionWrapper(
        F('value') * 100.0 / F('max_value'),
        output_field=FloatField()
    )
).aggregate(average=Avg('percentage'))
```

---

## 5. Cas d'Usage ML

### Créer un Modèle ML

```python
from apps.ml.models import MLModel
from django.utils import timezone
from decimal import Decimal

ml_model = MLModel.objects.create(
    name="Student Success Predictor",
    version="1.0.0",
    status='training',
    accuracy=Decimal('87.5'),
    precision=Decimal('85.2'),
    recall=Decimal('89.1'),
    f1_score=Decimal('87.1'),
    trained_at=timezone.now(),
    training_data_size=5000
)

# Activer le modèle
ml_model.activate()
print(f"Modèle actif: {ml_model.is_active()}")  # True
print(f"Score moyen: {ml_model.average_score:.2f}%")
```

### Créer une Prédiction

```python
from apps.predictions.models import Prediction

# Créer une prédiction
prediction = Prediction.objects.create(
    student=student,
    model_version=ml_model,
    risk_score=65,  # Le risk_level sera auto-calculé
    predicted_success_rate=70,
    factors=[
        {"name": "attendance", "impact": 0.35},
        {"name": "grades", "impact": 0.45},
        {"name": "engagement", "impact": 0.20}
    ]
)

print(f"Risk level: {prediction.risk_level}")  # 'high' (auto-calculé)
print(f"Student updated: {student.risk_level}")  # 'high' (auto-mis à jour)

# Récupérer les principaux facteurs
top_factors = prediction.get_top_factors(limit=3)
for factor in top_factors:
    print(f"- {factor['name']}: {factor['impact']:.2%}")
```

### Analyser les Prédictions

```python
# Dernières prédictions d'un étudiant
recent_predictions = Prediction.objects.filter(
    student=student
).select_related('model_version').order_by('-created_at')[:10]

# Prédictions critiques récentes
critical_predictions = Prediction.objects.filter(
    risk_level='critical',
    created_at__gte=timezone.now() - timezone.timedelta(days=7)
).select_related('student', 'student__program')

# Évolution du score de risque
risk_evolution = Prediction.objects.filter(
    student=student
).order_by('created_at').values('created_at', 'risk_score')
```

---

## 6. Gestion des Alertes

### Créer des Alertes

```python
from apps.alerts.models import Alert

# Méthode 1: Création directe
alert = Alert.objects.create(
    student=student,
    type='performance',
    level='high',
    message="Notes en baisse significative dans les matières principales",
    status='new'
)

# Méthode 2: Factory methods (recommandé)
performance_alert = Alert.create_performance_alert(
    student=student,
    message="Moyenne inférieure à 60% en mathématiques",
    level='high'
)

attendance_alert = Alert.create_attendance_alert(
    student=student,
    message="Taux de présence inférieur à 70%",
    level='medium'
)

risk_alert = Alert.create_risk_alert(
    student=student,
    message="Score de risque > 75, intervention urgente recommandée",
    level='critical'
)

prediction_alert = Alert.create_prediction_alert(
    student=student,
    message="Prédiction ML indique un risque élevé d'échec",
    level='high'
)
```

### Gérer les Alertes

```python
# Récupérer les alertes non traitées
new_alerts = Alert.objects.filter(
    status='new'
).select_related('student', 'student__program').order_by('-created_at')

# Récupérer les alertes critiques
critical_alerts = Alert.objects.filter(
    level='critical',
    status__in=['new', 'acknowledged']
)

# Traiter une alerte
alert = Alert.objects.get(id=alert_id)

# Accuser réception
alert.acknowledge()
print(f"Status: {alert.status}")  # 'acknowledged'

# Résoudre
alert.resolve()
print(f"Status: {alert.status}")  # 'resolved'
print(f"Résolu le: {alert.resolved_at}")

# Vérifications
if alert.is_new():
    print("Alerte nouvelle, action requise")

if alert.is_critical():
    print("Alerte critique, intervention urgente!")
```

### Statistiques d'Alertes

```python
# Alertes par type
alert_by_type = Alert.objects.values('type').annotate(
    count=Count('id')
).order_by('-count')

# Alertes par niveau
alert_by_level = Alert.objects.values('level').annotate(
    count=Count('id')
).order_by('-count')

# Alertes non résolues par programme
unresolved_by_program = Alert.objects.filter(
    status__in=['new', 'acknowledged']
).values(
    'student__program__name'
).annotate(
    count=Count('id')
).order_by('-count')

# Temps moyen de résolution
from django.db.models import Avg, F, ExpressionWrapper, DurationField

avg_resolution_time = Alert.objects.filter(
    status='resolved',
    resolved_at__isnull=False
).annotate(
    resolution_time=ExpressionWrapper(
        F('resolved_at') - F('created_at'),
        output_field=DurationField()
    )
).aggregate(Avg('resolution_time'))
```

---

## 7. Requêtes Complexes et Optimisations

### Optimisation avec select_related et prefetch_related

```python
# Mauvais: N+1 queries
students = Student.objects.all()
for student in students:
    print(student.program.name)  # Query à chaque itération
    print(student.session.name)  # Query à chaque itération

# Bon: 1 query avec JOINs
students = Student.objects.select_related(
    'program', 'session'
).all()
for student in students:
    print(student.program.name)  # Pas de query supplémentaire
    print(student.session.name)  # Pas de query supplémentaire

# Avec relations reverse (1:N)
students = Student.objects.prefetch_related(
    'grades', 'attendances', 'predictions', 'alerts'
).select_related('program', 'session')
```

### Agrégations Avancées

```python
from django.db.models import Avg, Count, Q, F, Case, When, IntegerField

# Performance dashboard pour un étudiant
student_dashboard = Student.objects.filter(
    id=student_id
).annotate(
    # Moyenne des notes
    avg_grade=Avg(
        ExpressionWrapper(
            F('grades__value') * 100.0 / F('grades__max_value'),
            output_field=FloatField()
        )
    ),
    # Nombre total de notes
    total_grades=Count('grades'),
    # Taux de présence
    attendance_rate=ExpressionWrapper(
        Count('attendances', filter=Q(attendances__status='present')) * 100.0 /
        Count('attendances'),
        output_field=FloatField()
    ),
    # Nombre d'alertes actives
    active_alerts=Count('alerts', filter=Q(alerts__status='new'))
).first()

print(f"Moyenne: {student_dashboard.avg_grade:.2f}%")
print(f"Présence: {student_dashboard.attendance_rate:.2f}%")
print(f"Alertes actives: {student_dashboard.active_alerts}")
```

### Requêtes Conditionnelles

```python
# Catégoriser les étudiants par performance
students_by_performance = Student.objects.annotate(
    avg_grade=Avg(
        ExpressionWrapper(
            F('grades__value') * 100.0 / F('grades__max_value'),
            output_field=FloatField()
        )
    ),
    performance_category=Case(
        When(avg_grade__gte=90, then='Excellent'),
        When(avg_grade__gte=80, then='Très Bien'),
        When(avg_grade__gte=70, then='Bien'),
        When(avg_grade__gte=60, then='Satisfaisant'),
        default='À Améliorer',
        output_field=models.CharField()
    )
).values('performance_category').annotate(count=Count('id'))
```

---

## 8. Transactions et Bulk Operations

### Opérations Bulk

```python
from django.db import transaction

# Bulk create (plus rapide que create() en boucle)
students = [
    Student(matricule=f"2024{i:03d}", first_name=f"Student{i}",
            last_name="Test", email=f"student{i}@test.com",
            date_of_birth=date(2000, 1, 1), program=program,
            session=session, status='active')
    for i in range(1, 101)
]
Student.objects.bulk_create(students, batch_size=100)

# Bulk update
students = Student.objects.filter(session=old_session)
for student in students:
    student.session = new_session
Student.objects.bulk_update(students, ['session'], batch_size=100)
```

### Transactions Atomiques

```python
# Assurer l'atomicité des opérations
with transaction.atomic():
    # Créer un étudiant
    student = Student.objects.create(...)

    # Créer ses notes
    grades = [...]
    Grade.objects.bulk_create(grades)

    # Générer une prédiction
    prediction = Prediction.objects.create(...)

    # Si une erreur se produit, tout est annulé (rollback)
```

---

## 9. Signals et Hooks

### Utilisation des Signals (exemple)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Prediction)
def create_alert_on_high_risk(sender, instance, created, **kwargs):
    """Créer automatiquement une alerte si risque élevé"""
    if created and instance.risk_level in ['high', 'critical']:
        Alert.create_risk_alert(
            student=instance.student,
            message=f"Nouvelle prédiction indique un risque {instance.risk_level}",
            level='high' if instance.risk_level == 'high' else 'critical'
        )
```

---

## Conseils de Performance

1. **Toujours utiliser select_related() pour ForeignKey**: Évite les N+1 queries
2. **Utiliser prefetch_related() pour relations reverse**: Optimise les 1:N
3. **Utiliser bulk_create() et bulk_update()**: Pour les opérations en masse
4. **Indexer les champs fréquemment filtrés**: Déjà fait dans les modèles
5. **Utiliser only() et defer()**: Pour récupérer seulement certains champs
6. **Utiliser values() et values_list()**: Pour récupérer seulement certains champs sous forme de dict/tuple
7. **Utiliser iterator()**: Pour les très grands querysets
8. **Cache les résultats fréquents**: Avec Django cache framework

---

**Note**: Tous ces exemples supposent que les migrations ont été exécutées et que la base de données est correctement configurée.
