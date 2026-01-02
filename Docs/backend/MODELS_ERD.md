# Entity Relationship Diagram (ERD) - SPAS Models

## Diagramme Complet des Relations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SYSTÈME SPAS - MODÈLES DJANGO                       │
└─────────────────────────────────────────────────────────────────────────────┘


┌──────────────────┐
│      User        │
│   (auth/users)   │
├──────────────────┤
│ • email (PK)     │
│ • first_name     │
│ • last_name      │
│ • role           │
│ • phone          │
│ • is_active      │
└──────────────────┘
   │
   │ (permissions)
   ▼
   [Gestion des permissions RBAC]


┌──────────────────┐         ┌──────────────────┐
│     Program      │◄───────►│     Subject      │
│   (programs)     │  M2M    │   (programs)     │
├──────────────────┤         ├──────────────────┤
│ • id (PK)        │         │ • id (PK)        │
│ • name           │         │ • name           │
│ • code (UK)      │         │ • code (UK)      │
│ • description    │         │ • description    │
│ • duration       │         └──────────────────┘
│ • status         │                │
└──────────────────┘                │
        │                           │
        │ (1:N)                     │ (1:N)
        ▼                           ▼


┌──────────────────┐         ┌──────────────────┐
│     Session      │         │      Grade       │
│   (sessions)     │         │    (grades)      │
├──────────────────┤         ├──────────────────┤
│ • id (PK)        │         │ • id (PK)        │
│ • name           │         │ • value          │
│ • year           │    ┌───►│ • max_value      │
│ • start_date     │    │    │ • type           │
│ • end_date       │    │    │ • date           │
│ • status         │    │    │ • student_id (FK)│
└──────────────────┘    │    │ • subject_id (FK)│
        │               │    │ • session_id (FK)│
        │ (1:N)         │    └──────────────────┘
        │               │
        ▼               │    ┌──────────────────┐
                        │    │   Attendance     │
┌──────────────────┐   │    │  (attendance)    │
│     Student      │   │    ├──────────────────┤
│   (students)     │   │    │ • id (PK)        │
├──────────────────┤   │    │ • date           │
│ • id (PK)        │   │    │ • status         │
│ • matricule (UK) │   │    │ • justification  │
│ • first_name     │───┼───►│ • student_id (FK)│
│ • last_name      │   │    │ • subject_id (FK)│
│ • email (UK)     │   │    └──────────────────┘
│ • phone          │   │
│ • date_of_birth  │   │
│ • status         │   │    ┌──────────────────┐
│ • risk_level     │   │    │   Prediction     │
│ • risk_score     │   │    │  (predictions)   │
│ • program_id (FK)│   │    ├──────────────────┤
│ • session_id (FK)│   │    │ • id (PK)        │
└──────────────────┘   │    │ • risk_score     │
        │              │    │ • risk_level     │
        │              │    │ • success_rate   │
        │              ├───►│ • factors (JSON) │
        │              │    │ • student_id (FK)│
        │              │    │ • model_ver (FK) │
        │              │    └──────────────────┘
        │              │            ▲
        │              │            │
        │              │            │ (N:1)
        │              │            │
        │              │    ┌──────────────────┐
        │              │    │    MLModel       │
        │              │    │      (ml)        │
        │              │    ├──────────────────┤
        │              │    │ • id (PK)        │
        │              │    │ • name           │
        │              │    │ • version        │
        │              │    │ • status         │
        │              │    │ • accuracy       │
        │              │    │ • precision      │
        │              │    │ • recall         │
        │              │    │ • f1_score       │
        │              │    │ • trained_at     │
        │              │    │ • training_size  │
        │              │    └──────────────────┘
        │              │
        │              │
        │              │    ┌──────────────────┐
        │              │    │      Alert       │
        │              │    │    (alerts)      │
        │              │    ├──────────────────┤
        │              │    │ • id (PK)        │
        │              │    │ • type           │
        │              │    │ • level          │
        │              │    │ • message        │
        │              └───►│ • status         │
        │                   │ • student_id (FK)│
        │                   │ • created_at     │
        │                   │ • acknowledged   │
        │                   │ • resolved_at    │
        │                   └──────────────────┘
        │
        ▼
  [Relations multiples vers Student]


═══════════════════════════════════════════════════════════════════════════════

LÉGENDE:
  • PK = Primary Key (Clé Primaire)
  • FK = Foreign Key (Clé Étrangère)
  • UK = Unique Key (Clé Unique)
  • M2M = Many-to-Many (Plusieurs-à-Plusieurs)
  • 1:N = One-to-Many (Un-à-Plusieurs)

═══════════════════════════════════════════════════════════════════════════════
```

## Relations Détaillées par Entité

### 1. Student (Hub Central)

Le modèle `Student` est le hub central du système avec les relations suivantes:

```
Student
  ├─> Program (FK, PROTECT)
  ├─> Session (FK, PROTECT)
  ├─< Grade (1:N)
  ├─< Attendance (1:N)
  ├─< Prediction (1:N)
  └─< Alert (1:N)
```

**Cardinalité**:
- Un étudiant appartient à UN programme
- Un étudiant appartient à UNE session
- Un étudiant peut avoir PLUSIEURS notes
- Un étudiant peut avoir PLUSIEURS présences
- Un étudiant peut avoir PLUSIEURS prédictions
- Un étudiant peut avoir PLUSIEURS alertes

### 2. Program

```
Program
  ├─< Student (1:N)
  └─<> Subject (M2M)
```

**Cardinalité**:
- Un programme peut avoir PLUSIEURS étudiants
- Un programme peut avoir PLUSIEURS matières
- Une matière peut être dans PLUSIEURS programmes

### 3. Subject

```
Subject
  ├─<> Program (M2M)
  ├─< Grade (1:N)
  └─< Attendance (1:N)
```

**Cardinalité**:
- Une matière peut être dans PLUSIEURS programmes
- Une matière peut avoir PLUSIEURS notes
- Une matière peut avoir PLUSIEURS enregistrements de présence

### 4. Session

```
Session
  ├─< Student (1:N)
  └─< Grade (1:N)
```

**Cardinalité**:
- Une session peut avoir PLUSIEURS étudiants
- Une session peut avoir PLUSIEURS notes

### 5. Grade

```
Grade
  ├─> Student (FK, CASCADE)
  ├─> Subject (FK, PROTECT)
  └─> Session (FK, PROTECT)
```

**Cardinalité**:
- Une note appartient à UN étudiant
- Une note est pour UNE matière
- Une note est dans UNE session

### 6. Attendance

```
Attendance
  ├─> Student (FK, CASCADE)
  └─> Subject (FK, PROTECT)
```

**Cardinalité**:
- Une présence appartient à UN étudiant
- Une présence est pour UNE matière

**Contrainte**: Unique ensemble (student, subject, date)

### 7. MLModel

```
MLModel
  └─< Prediction (1:N)
```

**Cardinalité**:
- Un modèle ML peut générer PLUSIEURS prédictions

### 8. Prediction

```
Prediction
  ├─> Student (FK, CASCADE)
  └─> MLModel (FK, PROTECT)
```

**Cardinalité**:
- Une prédiction appartient à UN étudiant
- Une prédiction utilise UN modèle ML

**Effet secondaire**: Met à jour Student.risk_level et Student.risk_score

### 9. Alert

```
Alert
  └─> Student (FK, CASCADE)
```

**Cardinalité**:
- Une alerte concerne UN étudiant

### 10. User

```
User (AbstractUser)
  [Aucune relation FK directe avec les autres modèles]
  [Gestion des permissions via Django Auth]
```

**Rôles**:
- admin
- teacher
- ds (Directeur des Études)
- pedagogical (Conseiller Pédagogique)

## Flux de Données Typiques

### Flux 1: Création d'un Étudiant

```
1. Création Program
2. Création Session
3. Création Student (référence Program + Session)
```

### Flux 2: Enregistrement d'une Note

```
1. Student existe
2. Subject existe
3. Session existe
4. Création Grade (références Student + Subject + Session)
```

### Flux 3: Génération d'une Prédiction ML

```
1. MLModel entraîné existe
2. Student avec données (grades, attendance) existe
3. Création Prediction (analyse des données)
4. Mise à jour automatique de Student.risk_level et Student.risk_score
5. (Optionnel) Création Alert si risque élevé
```

### Flux 4: Gestion des Alertes

```
1. Détection d'un problème (note faible, absence, prédiction risque)
2. Création Alert (type, level, message)
3. Alert.status = 'new'
4. Utilisateur acknowledge → Alert.status = 'acknowledged'
5. Action prise → Alert.status = 'resolved'
```

## Indexes Critiques

### Indexes sur Student
```sql
- matricule (UNIQUE)
- email (UNIQUE)
- status
- risk_level
- (program, session) composite
```

### Indexes sur Grade
```sql
- (student, subject) composite
- (student, session) composite
- (subject, session) composite
- date (DESC)
- type
```

### Indexes sur Attendance
```sql
- (student, date) composite
- (subject, date) composite
- (status, date) composite
- date (DESC)
- UNIQUE (student, subject, date)
```

### Indexes sur Prediction
```sql
- (student, created_at) composite
- risk_level
- created_at (DESC)
- (model_version, created_at) composite
```

### Indexes sur Alert
```sql
- (student, status) composite
- (type, level) composite
- (status, created_at) composite
- created_at (DESC)
```

## Politiques de Suppression (ON DELETE)

| Relation | Politique | Raison |
|----------|-----------|---------|
| Student → Program | PROTECT | Ne pas supprimer un programme avec des étudiants |
| Student → Session | PROTECT | Ne pas supprimer une session avec des étudiants |
| Grade → Student | CASCADE | Les notes sont supprimées avec l'étudiant |
| Grade → Subject | PROTECT | Ne pas supprimer une matière avec des notes |
| Grade → Session | PROTECT | Ne pas supprimer une session avec des notes |
| Attendance → Student | CASCADE | Les présences sont supprimées avec l'étudiant |
| Attendance → Subject | PROTECT | Ne pas supprimer une matière avec des présences |
| Prediction → Student | CASCADE | Les prédictions sont supprimées avec l'étudiant |
| Prediction → MLModel | PROTECT | Ne pas supprimer un modèle avec des prédictions |
| Alert → Student | CASCADE | Les alertes sont supprimées avec l'étudiant |

## Requêtes Complexes Typiques

### 1. Étudiants à Risque

```python
# Étudiants avec risk_level HIGH ou CRITICAL
students_at_risk = Student.objects.filter(
    risk_level__in=['high', 'critical']
).select_related('program', 'session')
```

### 2. Moyenne des Notes par Étudiant

```python
from django.db.models import Avg, F, ExpressionWrapper, FloatField

# Moyenne pondérée des notes
student_averages = Grade.objects.filter(
    student_id=student_id
).annotate(
    percentage=ExpressionWrapper(
        F('value') * 100.0 / F('max_value'),
        output_field=FloatField()
    )
).aggregate(Avg('percentage'))
```

### 3. Taux de Présence par Étudiant

```python
from django.db.models import Count, Q

# Taux de présence
attendance_stats = Attendance.objects.filter(
    student_id=student_id
).aggregate(
    total=Count('id'),
    present=Count('id', filter=Q(status='present')),
    absent=Count('id', filter=Q(status='absent'))
)

attendance_rate = (attendance_stats['present'] / attendance_stats['total']) * 100
```

### 4. Alertes Non Résolues par Niveau

```python
# Alertes critiques non résolues
critical_alerts = Alert.objects.filter(
    level='critical',
    status__in=['new', 'acknowledged']
).select_related('student', 'student__program').order_by('-created_at')
```

### 5. Prédictions Récentes avec Facteurs

```python
# Dernières prédictions avec leurs facteurs
recent_predictions = Prediction.objects.filter(
    student_id=student_id
).select_related(
    'student', 'model_version'
).order_by('-created_at')[:5]

# Accès aux facteurs
for pred in recent_predictions:
    top_factors = pred.get_top_factors(limit=3)
```

## Intégrité Référentielle

### Contraintes Uniques

1. **Student**: `matricule`, `email`
2. **Program**: `code`
3. **Subject**: `code`
4. **Session**: `(name, year)` ensemble
5. **Attendance**: `(student, subject, date)` ensemble
6. **MLModel**: `(name, version)` ensemble

### Validation des Données

- Scores (0-100): Validators sur risk_score, grades, métriques ML
- Emails: EmailField avec validation automatique
- Dates: DateField avec validation de format
- Choix: TextChoices pour type-safety
- Relations: ForeignKey avec vérification d'existence

---

**Ce diagramme ERD représente la structure complète et finale de la base de données SPAS.**
