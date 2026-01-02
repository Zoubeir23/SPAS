# Index des Fichiers Backend SPAS

Ce document liste tous les fichiers importants du backend avec leurs chemins absolus et descriptions.

---

## Configuration Principale

### C:\Users\Public\Libraries\one\SPAS\backend\config\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation package config, import Celery app |
| `settings.py` | **Configuration Django complète** - DB, DRF, JWT, CORS, Celery, logging |
| `urls.py` | **Routage principal API** - Auth JWT, documentation, routes apps |
| `celery.py` | Configuration Celery pour tâches asynchrones |
| `exceptions.py` | Gestionnaire d'exceptions personnalisé DRF |
| `wsgi.py` | Configuration WSGI pour déploiement production |

---

## Applications Django

### 1. Users - C:\Users\Public\Libraries\one\SPAS\backend\apps\users\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app users |
| `models.py` | **User model** - Utilisateur personnalisé avec rôles (ADMIN, TEACHER, ADVISOR, COORDINATOR) |
| `serializers.py` | UserSerializer, ChangePasswordSerializer |
| `views.py` | UserViewSet - Profil, changement password |
| `urls.py` | Routes API users |
| `admin.py` | Interface admin Django pour User |
| `apps.py` | Configuration app Django |
| `management/commands/init_spas.py` | **Commande initialisation** - Créer données initiales |

**Modèles**: User

---

### 2. Students - C:\Users\Public\Libraries\one\SPAS\backend\apps\students\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app students |
| `models.py` | **Student model** - Étudiant avec risk_level et risk_score |
| `serializers.py` | StudentSerializer |
| `views.py` | StudentViewSet - CRUD + endpoint at_risk |
| `urls.py` | Routes API students |
| `admin.py` | Interface admin Django pour Student |
| `apps.py` | Configuration app Django |
| `tests.py` | **Tests unitaires** pour Student model et API |

**Modèles**: Student

---

### 3. Programs - C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app programs |
| `models.py` | **Program et Course models** - Programmes et cours |
| `serializers.py` | ProgramSerializer, CourseSerializer |
| `views.py` | ProgramViewSet, CourseViewSet |
| `urls.py` | Routes API programs et courses |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |

**Modèles**: Program, Course

---

### 4. Sessions - C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app sessions |
| `models.py` | **AcademicPeriod, CourseSession, Enrollment models** |
| `serializers.py` | Serializers pour tous les modèles |
| `views.py` | AcademicPeriodViewSet, CourseSessionViewSet, EnrollmentViewSet |
| `urls.py` | Routes API sessions |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |

**Modèles**: AcademicPeriod, CourseSession, Enrollment

---

### 5. Grades - C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app grades |
| `models.py` | **Grade, CourseGradeSummary models** - Calculs automatiques notes |
| `serializers.py` | GradeSerializer, CourseGradeSummarySerializer |
| `views.py` | GradeViewSet, CourseGradeSummaryViewSet - Endpoint failing_students |
| `urls.py` | Routes API grades |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |

**Modèles**: Grade, CourseGradeSummary

---

### 6. Attendance - C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app attendance |
| `models.py` | **AttendanceRecord, AttendanceSummary models** - Calcul taux présence |
| `serializers.py` | AttendanceRecordSerializer, AttendanceSummarySerializer |
| `views.py` | ViewSets - Endpoint bulk_create, low_attendance |
| `urls.py` | Routes API attendance |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |

**Modèles**: AttendanceRecord, AttendanceSummary

---

### 7. ML - C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app ml |
| `models.py` | **MLModel, TrainingJob models** - Gestion modèles ML |
| `serializers.py` | MLModelSerializer, TrainingJobSerializer |
| `views.py` | MLModelViewSet - Endpoints train, activate |
| `urls.py` | Routes API ml |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |
| `tasks.py` | **Tâches Celery** - train_model_task |

**Modèles**: MLModel, TrainingJob
**Tâches Celery**: train_model_task

---

### 8. Predictions - C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app predictions |
| `models.py` | **Prediction, RecommendedIntervention models** - Prédictions risque |
| `serializers.py` | PredictionSerializer, RecommendedInterventionSerializer |
| `views.py` | PredictionViewSet - Endpoints at_risk, generate_bulk, statistics |
| `urls.py` | Routes API predictions |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |
| `tasks.py` | **Tâches Celery** - generate_predictions_task |

**Modèles**: Prediction, RecommendedIntervention
**Tâches Celery**: generate_predictions_task

---

### 9. Alerts - C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation app alerts |
| `models.py` | **Alert, AlertAction models** - Système alertes et workflow |
| `serializers.py` | AlertSerializer, AlertActionSerializer |
| `views.py` | AlertViewSet - Endpoints my_alerts, critical, acknowledge, resolve, assign |
| `urls.py` | Routes API alerts |
| `admin.py` | Interface admin Django |
| `apps.py` | Configuration app Django |
| `tasks.py` | **Tâches Celery** - create_alerts_from_predictions, check_low_attendance, check_failing_grades |

**Modèles**: Alert, AlertAction
**Tâches Celery**: create_alerts_from_predictions, check_low_attendance, check_failing_grades

---

## Scripts Utilitaires

### C:\Users\Public\Libraries\one\SPAS\backend\scripts\

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialisation package scripts |
| `create_sample_data.py` | **Script création données de test** - Génère étudiants, notes, présences |

---

## Fichiers Racine

### C:\Users\Public\Libraries\one\SPAS\backend\

| Fichier | Description |
|---------|-------------|
| `manage.py` | **Django management** - Commandes Django (runserver, migrate, etc.) |
| `requirements.txt` | **Dépendances Python** - Toutes les librairies nécessaires |
| `.env.example` | **Template variables d'environnement** - À copier en .env |
| `.env` | Variables d'environnement (git-ignored, créer manuellement) |
| `.gitignore` | Fichiers ignorés par Git |
| `Dockerfile` | **Image Docker backend** - Pour containerisation |
| `docker-compose.yml` | **Services Docker** - PostgreSQL, Redis, Backend, Celery |
| `pytest.ini` | Configuration pytest pour tests |

---

## Scripts Déploiement Windows

### C:\Users\Public\Libraries\one\SPAS\backend\

| Fichier | Description |
|---------|-------------|
| `setup_dev.bat` | Script installation Windows (Batch) |
| `setup_dev.ps1` | Script installation Windows (PowerShell) |
| `run_dev.bat` | Script démarrage serveur développement |

---

## Documentation

### C:\Users\Public\Libraries\one\SPAS\backend\

| Fichier | Description |
|---------|-------------|
| `README.md` | **Documentation principale** - Installation et utilisation |
| `QUICKSTART.md` | **Guide démarrage rapide** - Setup en 5 minutes |
| `API_GUIDE.md` | **Documentation API complète** - Tous les endpoints détaillés |
| `PROJECT_SUMMARY.md` | Résumé du projet et architecture |
| `CHANGELOG.md` | Historique des modifications |
| `RAPPORT_IMPLEMENTATION_BACKEND.md` | **Rapport implémentation détaillé** - État actuel backend |
| `STRUCTURE_BACKEND.md` | **Structure complète backend** - Ce document |
| `INDEX_FICHIERS.md` | **Index fichiers** - Liste tous les fichiers (ce document) |

---

## Fichiers de Configuration VSCode

### C:\Users\Public\Libraries\one\SPAS\backend\.vscode\

Configuration pour Visual Studio Code (settings, launch, extensions recommandées)

---

## Résumé par Type de Fichier

### Modèles Django (models.py) - 9 fichiers

1. `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\models.py` - User
2. `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\models.py` - Student
3. `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\models.py` - Program, Course
4. `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\models.py` - AcademicPeriod, CourseSession, Enrollment
5. `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\models.py` - Grade, CourseGradeSummary
6. `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\models.py` - AttendanceRecord, AttendanceSummary
7. `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\models.py` - MLModel, TrainingJob
8. `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\models.py` - Prediction, RecommendedIntervention
9. `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\models.py` - Alert, AlertAction

**Total**: 17 modèles de données

---

### Serializers (serializers.py) - 9 fichiers

1. `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\serializers.py`
2. `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\serializers.py`
3. `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\serializers.py`
4. `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\serializers.py`
5. `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\serializers.py`
6. `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\serializers.py`
7. `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\serializers.py`
8. `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\serializers.py`
9. `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\serializers.py`

**Total**: 20+ serializers

---

### ViewSets (views.py) - 9 fichiers

1. `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\views.py` - UserViewSet
2. `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\views.py` - StudentViewSet
3. `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\views.py` - ProgramViewSet, CourseViewSet
4. `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\views.py` - AcademicPeriodViewSet, CourseSessionViewSet, EnrollmentViewSet
5. `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\views.py` - GradeViewSet, CourseGradeSummaryViewSet
6. `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\views.py` - AttendanceRecordViewSet, AttendanceSummaryViewSet
7. `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\views.py` - MLModelViewSet, TrainingJobViewSet
8. `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\views.py` - PredictionViewSet, RecommendedInterventionViewSet
9. `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\views.py` - AlertViewSet, AlertActionViewSet

**Total**: 17 ViewSets

---

### URLs (urls.py) - 10 fichiers

1. `C:\Users\Public\Libraries\one\SPAS\backend\config\urls.py` - **Routage principal**
2. `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\urls.py`
3. `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\urls.py`
4. `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\urls.py`
5. `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\urls.py`
6. `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\urls.py`
7. `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\urls.py`
8. `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\urls.py`
9. `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\urls.py`
10. `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\urls.py`

---

### Tâches Celery (tasks.py) - 3 fichiers

1. `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\tasks.py`
   - `train_model_task` - Entraîner modèle ML

2. `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\tasks.py`
   - `generate_predictions_task` - Générer prédictions

3. `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\tasks.py`
   - `create_alerts_from_predictions` - Créer alertes depuis prédictions
   - `check_low_attendance` - Vérifier présences faibles
   - `check_failing_grades` - Vérifier notes insuffisantes

**Total**: 5 tâches asynchrones

---

### Admin (admin.py) - 9 fichiers

Configuration interface admin Django pour tous les modèles

1. `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\admin.py`
2. `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\admin.py`
3. `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\admin.py`
4. `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\admin.py`
5. `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\admin.py`
6. `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\admin.py`
7. `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\admin.py`
8. `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\admin.py`
9. `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\admin.py`

---

### Tests (tests.py) - 1+ fichiers

1. `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\tests.py` - Tests étudiants

**Note**: Tests à ajouter pour autres apps

---

## Chemins Absolus Clés

### Fichiers de configuration critiques

```
C:\Users\Public\Libraries\one\SPAS\backend\config\settings.py
C:\Users\Public\Libraries\one\SPAS\backend\config\urls.py
C:\Users\Public\Libraries\one\SPAS\backend\.env
C:\Users\Public\Libraries\one\SPAS\backend\requirements.txt
C:\Users\Public\Libraries\one\SPAS\backend\manage.py
```

### Modèles principaux

```
C:\Users\Public\Libraries\one\SPAS\backend\apps\users\models.py
C:\Users\Public\Libraries\one\SPAS\backend\apps\students\models.py
C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\models.py
C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\models.py
```

### Tâches asynchrones

```
C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\tasks.py
C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\tasks.py
C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\tasks.py
```

### Documentation

```
C:\Users\Public\Libraries\one\SPAS\backend\README.md
C:\Users\Public\Libraries\one\SPAS\backend\API_GUIDE.md
C:\Users\Public\Libraries\one\SPAS\backend\STRUCTURE_BACKEND.md
C:\Users\Public\Libraries\one\SPAS\backend\RAPPORT_IMPLEMENTATION_BACKEND.md
```

---

## Navigation Rapide par Fonctionnalité

### Authentification & Utilisateurs
- Modèle: `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\models.py`
- Views: `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\views.py`
- Config JWT: `C:\Users\Public\Libraries\one\SPAS\backend\config\settings.py` (lignes 172-187)

### Gestion Étudiants
- Modèle: `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\models.py`
- Views: `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\views.py`
- Tests: `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\tests.py`

### Système de Notes
- Modèles: `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\models.py`
- Calculs: Voir méthodes `save()` dans Grade et CourseGradeSummary
- Views: `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\views.py`

### Prédictions ML
- Modèles: `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\models.py`
- Tâche génération: `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\tasks.py`
- Views: `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\views.py`

### Alertes
- Modèles: `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\models.py`
- Tâches auto: `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\tasks.py`
- Views: `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\views.py`

---

## Ordre de Lecture Recommandé

Pour comprendre le backend, lire dans cet ordre:

1. **Configuration**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\config\settings.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\config\urls.py`

2. **Authentification**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\views.py`

3. **Données de base**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\models.py`

4. **Données académiques**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\models.py`

5. **Machine Learning**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\tasks.py`

6. **Prédictions**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\tasks.py`

7. **Alertes**:
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\models.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\tasks.py`
   - `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\views.py`

---

## Statistiques Fichiers

- **Fichiers Python (.py)**: ~80 fichiers
- **Applications Django**: 9
- **Modèles de données**: 17
- **ViewSets**: 17
- **Serializers**: 20+
- **Tâches Celery**: 5
- **Fichiers de documentation**: 8
- **Fichiers de configuration**: 6

---

**Dernière mise à jour**: 2026-01-02
**Version**: 1.0.0
