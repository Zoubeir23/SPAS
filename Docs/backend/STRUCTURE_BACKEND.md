# Structure Complète du Backend SPAS

## Vue d'ensemble

Le backend SPAS est une API REST complète construite avec Django 5.x et Django REST Framework. Il implémente un système prédictif d'alerte scolaire avec 9 applications Django interconnectées.

---

## Architecture Globale

```
backend/
├── config/                      # Configuration principale Django
│   ├── __init__.py             # Import Celery app
│   ├── settings.py             # Configuration Django complète
│   ├── urls.py                 # Routage principal API
│   ├── celery.py               # Configuration Celery
│   ├── exceptions.py           # Gestionnaire d'exceptions personnalisé
│   └── wsgi.py                 # Configuration WSGI
│
├── apps/                        # Applications Django (9 apps)
│   ├── __init__.py
│   ├── users/                  # Gestion utilisateurs & authentification
│   ├── students/               # Gestion étudiants
│   ├── programs/               # Programmes & cours
│   ├── sessions/               # Sessions académiques & inscriptions
│   ├── grades/                 # Notes & évaluations
│   ├── attendance/             # Présences & absences
│   ├── ml/                     # Modèles ML & entraînement
│   ├── predictions/            # Prédictions & interventions
│   └── alerts/                 # Alertes & actions
│
├── scripts/                     # Scripts utilitaires
│   └── create_sample_data.py   # Création données de test
│
├── static/                      # Fichiers statiques
├── media/                       # Fichiers uploadés
├── logs/                        # Logs application
├── ml_models/                   # Modèles ML sérialisés
│
├── manage.py                    # Django management
├── requirements.txt             # Dépendances Python
├── .env.example                 # Template variables d'environnement
├── .env                         # Variables d'environnement (git-ignored)
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Image Docker
├── docker-compose.yml           # Services Docker
├── pytest.ini                   # Configuration tests
│
└── Documentation/
    ├── README.md               # Documentation principale
    ├── QUICKSTART.md           # Guide démarrage rapide
    ├── API_GUIDE.md            # Documentation API complète
    ├── PROJECT_SUMMARY.md      # Résumé du projet
    ├── CHANGELOG.md            # Historique changements
    └── RAPPORT_IMPLEMENTATION_BACKEND.md  # Rapport implémentation
```

---

## Applications Django (9/9)

### 1. **users** - Authentification & Utilisateurs

**Responsabilité**: Gestion des utilisateurs du système avec authentification JWT

**Modèles**:
- `User` - Utilisateur personnalisé (AbstractUser)
  - Authentification par email (pas username)
  - Rôles: ADMIN, TEACHER, ADVISOR, COORDINATOR
  - Champs: email, first_name, last_name, role, phone, department

**Endpoints principaux**:
- `POST /api/auth/token/` - Obtenir JWT token
- `POST /api/auth/token/refresh/` - Rafraîchir token
- `GET /api/users/me/` - Profil utilisateur actuel
- `PUT /api/users/update_profile/` - Modifier profil
- `POST /api/users/change_password/` - Changer mot de passe

**Fichiers clés**:
- `models.py` - User model avec UserManager
- `serializers.py` - UserSerializer, ChangePasswordSerializer
- `views.py` - UserViewSet avec actions personnalisées
- `management/commands/init_spas.py` - Commande initialisation

---

### 2. **students** - Gestion Étudiants

**Responsabilité**: CRUD étudiants avec évaluation du risque

**Modèles**:
- `Student` - Étudiant
  - Statuts: ACTIVE, INACTIVE, GRADUATED
  - Niveaux de risque: LOW, MEDIUM, HIGH
  - Champs: matricule, first_name, last_name, email, phone, date_of_birth
  - Relations: program (FK), session (FK)
  - Évaluation risque: risk_level, risk_score (0-100)

**Endpoints principaux**:
- `GET /api/students/` - Liste étudiants (filtres: status, program, risk_level)
- `POST /api/students/` - Créer étudiant
- `GET /api/students/{id}/` - Détails étudiant
- `PUT /api/students/{id}/` - Modifier étudiant
- `GET /api/students/at_risk/` - Étudiants à risque (HIGH/MEDIUM)

**Fonctionnalités**:
- Recherche full-text (matricule, nom, email)
- Filtrage par statut et programme
- Indexation DB sur champs clés
- Méthode `update_risk_assessment()` pour ML

---

### 3. **programs** - Programmes & Cours

**Responsabilité**: Gestion catalogue académique

**Modèles**:
- `Program` - Programme d'études
  - Champs: code, name, duration_years, required_credits, description

- `Course` - Cours
  - Champs: code, name, credits, is_required, prerequisites (JSON), description
  - Relations: program (FK)

**Endpoints principaux**:
- `GET /api/programs/programs/` - Liste programmes
- `POST /api/programs/programs/` - Créer programme
- `GET /api/programs/courses/` - Liste cours
- `POST /api/programs/courses/` - Créer cours
- Filtres: par programme, par code

**Fonctionnalités**:
- Gestion prérequis de cours (JSON)
- Validation crédits requis

---

### 4. **sessions** - Sessions Académiques

**Responsabilité**: Gestion périodes académiques et inscriptions

**Modèles**:
- `AcademicPeriod` - Période académique
  - Saisons: WINTER, SUMMER, FALL
  - Champs: year, season, start_date, end_date, is_current

- `CourseSession` - Offre de cours
  - Champs: course, period, teacher, classroom, schedule, capacity, enrolled_count
  - Relations: course (FK), period (FK), teacher (FK to User)

- `Enrollment` - Inscription étudiant-cours
  - Statuts: ENROLLED, DROPPED, COMPLETED
  - Champs: student, course_session, enrollment_date, status
  - Relations: student (FK), course_session (FK)

**Endpoints principaux**:
- `GET /api/sessions/periods/` - Liste périodes
- `GET /api/sessions/periods/current/` - Période actuelle
- `GET /api/sessions/course-sessions/` - Sessions de cours
- `POST /api/sessions/enrollments/` - Inscrire étudiant
- Filtres: par période, par cours, par étudiant

**Fonctionnalités**:
- Gestion capacités cours
- Tracking inscriptions actives
- Validation contraintes d'inscription

---

### 5. **grades** - Notes & Évaluations

**Responsabilité**: Gestion notes avec calculs automatiques

**Modèles**:
- `Grade` - Note d'évaluation
  - Champs: student, course_session, evaluation_name, score (0-100), weight, date
  - Calcul auto: weighted_grade (score * weight)

- `CourseGradeSummary` - Résumé notes par cours
  - Champs calculés automatiquement:
    - final_score (moyenne pondérée)
    - letter_grade (A+, A, B+, etc.)
    - gpa (4.0 scale)
    - is_passing (>= 60%)

**Endpoints principaux**:
- `GET /api/grades/grades/` - Liste notes
- `POST /api/grades/grades/` - Créer note
- `GET /api/grades/summaries/` - Résumés notes
- `GET /api/grades/summaries/failing_students/` - Étudiants en échec
- `GET /api/grades/statistics/` - Statistiques globales

**Fonctionnalités**:
- Calcul automatique notes pondérées
- Conversion notes en lettres
- Détection étudiants en difficulté
- Statistiques par cours/programme

**Barème de conversion**:
```
A+ : 95-100  (4.0)
A  : 90-94   (4.0)
A- : 85-89   (3.7)
B+ : 80-84   (3.3)
B  : 75-79   (3.0)
B- : 70-74   (2.7)
C+ : 65-69   (2.3)
C  : 60-64   (2.0)
D  : 50-59   (1.0)
F  : 0-49    (0.0)
```

---

### 6. **attendance** - Présences

**Responsabilité**: Suivi présences avec calculs automatiques

**Modèles**:
- `AttendanceRecord` - Enregistrement présence
  - Statuts: PRESENT, ABSENT, LATE, EXCUSED
  - Champs: student, course_session, date, status, notes

- `AttendanceSummary` - Résumé présences
  - Champs calculés auto:
    - total_classes, present_count, absent_count, late_count, excused_count
    - attendance_rate (présent/total * 100)

**Endpoints principaux**:
- `GET /api/attendance/records/` - Enregistrements
- `POST /api/attendance/records/` - Créer enregistrement
- `POST /api/attendance/records/bulk_create/` - Création en masse
- `GET /api/attendance/summaries/` - Résumés
- `GET /api/attendance/summaries/low_attendance/` - Présence < 70%

**Fonctionnalités**:
- Prise de présence individuelle ou en masse
- Calcul automatique taux de présence
- Détection absentéisme
- Filtres par cours/date/étudiant

---

### 7. **ml** - Machine Learning

**Responsabilité**: Gestion modèles ML et entraînement

**Modèles**:
- `MLModel` - Modèle ML
  - Champs: name, version, model_type, is_active
  - Métriques: accuracy, precision, recall, f1_score
  - Stockage: model_file (FileField)

- `TrainingJob` - Job d'entraînement
  - Statuts: PENDING, RUNNING, COMPLETED, FAILED
  - Champs: model, status, parameters (JSON), metrics (JSON)
  - Suivi: started_at, completed_at, error_message

**Endpoints principaux**:
- `GET /api/ml/models/` - Liste modèles
- `POST /api/ml/models/` - Créer modèle
- `POST /api/ml/models/{id}/train/` - Entraîner modèle (async)
- `POST /api/ml/models/{id}/activate/` - Activer modèle
- `GET /api/ml/training-jobs/` - Jobs d'entraînement

**Tâches Celery**:
- `train_model_task(model_id, parameters)` - Entraîner modèle ML
  - Charge données training
  - Entraîne modèle
  - Calcule métriques
  - Sauvegarde modèle

**Fonctionnalités**:
- Entraînement asynchrone
- Versioning modèles
- Activation/désactivation
- Tracking métriques performance

---

### 8. **predictions** - Prédictions & Interventions

**Responsabilité**: Génération prédictions risque abandon

**Modèles**:
- `Prediction` - Prédiction risque
  - Niveaux: LOW, MEDIUM, HIGH, CRITICAL
  - Champs: student, model, risk_score (0-100), risk_level, confidence
  - contributing_factors (JSON): facteurs contributifs

- `RecommendedIntervention` - Intervention recommandée
  - Champs: prediction, intervention_type, priority, estimated_impact, description

**Endpoints principaux**:
- `GET /api/predictions/predictions/` - Liste prédictions
- `GET /api/predictions/predictions/at_risk/` - Étudiants à risque
- `POST /api/predictions/predictions/generate_bulk/` - Génération masse (async)
- `GET /api/predictions/predictions/statistics/` - Statistiques
- `GET /api/predictions/interventions/` - Interventions recommandées

**Tâches Celery**:
- `generate_predictions_task(period_id=None)` - Générer prédictions
  - Charge modèle actif
  - Extrait features étudiants
  - Génère prédictions
  - Sauvegarde résultats
  - Met à jour risk_score étudiants

**Fonctionnalités**:
- Génération prédictions en temps réel
- Génération en masse asynchrone
- Facteurs contributifs explicables
- Recommandations d'intervention
- Statistiques risque

**Seuils de risque**:
```
CRITICAL: score >= 80
HIGH:     score >= 60
MEDIUM:   score >= 40
LOW:      score < 40
```

---

### 9. **alerts** - Alertes & Actions

**Responsabilité**: Système d'alertes et workflow d'intervention

**Modèles**:
- `Alert` - Alerte
  - Types: DROPOUT_RISK, LOW_GRADES, LOW_ATTENDANCE, BEHAVIORAL
  - Sévérités: LOW, MEDIUM, HIGH, CRITICAL
  - Statuts: ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
  - Champs: student, alert_type, severity, status, assigned_to
  - Workflow: created_at, acknowledged_at, resolved_at

- `AlertAction` - Action sur alerte
  - Champs: alert, action_type, description, performed_by, performed_at

**Endpoints principaux**:
- `GET /api/alerts/alerts/` - Liste alertes
- `POST /api/alerts/alerts/` - Créer alerte
- `GET /api/alerts/alerts/my_alerts/` - Alertes assignées à moi
- `GET /api/alerts/alerts/critical/` - Alertes critiques
- `POST /api/alerts/alerts/{id}/acknowledge/` - Accuser réception
- `POST /api/alerts/alerts/{id}/resolve/` - Résoudre alerte
- `POST /api/alerts/alerts/{id}/assign/` - Assigner alerte
- `GET /api/alerts/actions/` - Historique actions

**Tâches Celery**:
- `create_alerts_from_predictions()` - Créer alertes depuis prédictions HIGH/CRITICAL
- `check_low_attendance()` - Vérifier présences < 70%
- `check_failing_grades()` - Vérifier notes < 60%

**Workflow alerte**:
1. ACTIVE - Alerte créée (auto ou manuelle)
2. ACKNOWLEDGED - Prise en compte par responsable
3. RESOLVED - Problème résolu avec action documentée
4. DISMISSED - Alerte rejetée (fausse alerte)

**Fonctionnalités**:
- Création automatique alertes (Celery)
- Assignation aux conseillers
- Workflow complet de résolution
- Historique actions
- Notifications (à implémenter)

---

## Stack Technique

### Backend Framework
- **Django 5.0+** - Framework web Python
- **Django REST Framework 3.15+** - API REST
- **Simple JWT 5.3+** - Authentification JWT

### Base de Données
- **PostgreSQL 14+** - Base de données principale
- **Indexes** - Sur champs clés (matricule, email, status, etc.)
- **Constraints** - Foreign keys, unique constraints

### Cache & Tâches Asynchrones
- **Redis 7+** - Cache et broker messages
- **Celery 5.3+** - Tâches asynchrones
  - Worker: `celery -A config worker -l info`
  - Beat: `celery -A config beat -l info` (tâches planifiées)

### Machine Learning
- **scikit-learn 1.3+** - Modèles ML
- **pandas 2.0+** - Manipulation données
- **numpy 1.24+** - Calculs numériques

### Documentation
- **drf-spectacular 0.27+** - OpenAPI 3.0 schema
- **Swagger UI** - Documentation interactive
- **ReDoc** - Documentation alternative

### Sécurité
- **CORS** - Configuration pour frontend React
- **JWT** - Authentification stateless
- **HTTPS** - Obligatoire en production
- **Validation** - Serializers DRF
- **Permissions** - Par rôle (RBAC)

### Déploiement
- **Docker** - Containerisation
- **Gunicorn** - WSGI server production
- **Whitenoise** - Serving fichiers statiques
- **PostgreSQL** - Base données production
- **Redis** - Cache production

---

## Configuration Environnement

### Variables d'environnement (.env)

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=spas_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60        # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440     # minutes (24h)

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# ML
ML_MODEL_PATH=ml_models/
ML_PREDICTION_THRESHOLD=0.7
```

---

## Permissions & Authentification

### Système de permissions

**Authentification**:
- JWT tokens avec access/refresh
- Header: `Authorization: Bearer <access_token>`

**Rôles utilisateurs**:
- **ADMIN** - Accès complet
- **COORDINATOR** - Gestion complète étudiants/alertes
- **ADVISOR** - Consultation et intervention
- **TEACHER** - Gestion notes/présences

**Permissions DRF**:
- Par défaut: `IsAuthenticated`
- Personnalisées par ViewSet selon rôle
- Actions admin: `IsAdminUser`

---

## API Endpoints Résumé

### Authentification
```
POST   /api/auth/token/              # Login JWT
POST   /api/auth/token/refresh/      # Refresh token
POST   /api/auth/token/verify/       # Verify token
```

### Utilisateurs
```
GET    /api/users/                   # Liste utilisateurs
GET    /api/users/me/                # Mon profil
PUT    /api/users/update_profile/    # Modifier profil
POST   /api/users/change_password/   # Changer password
```

### Étudiants
```
GET    /api/students/                # Liste étudiants
POST   /api/students/                # Créer étudiant
GET    /api/students/{id}/           # Détails
PUT    /api/students/{id}/           # Modifier
DELETE /api/students/{id}/           # Supprimer
GET    /api/students/at_risk/        # Étudiants à risque
```

### Programmes & Cours
```
GET    /api/programs/programs/       # Programmes
GET    /api/programs/courses/        # Cours
```

### Sessions & Inscriptions
```
GET    /api/sessions/periods/        # Périodes académiques
GET    /api/sessions/periods/current/# Période actuelle
GET    /api/sessions/course-sessions/# Sessions cours
GET    /api/sessions/enrollments/    # Inscriptions
```

### Notes
```
GET    /api/grades/grades/           # Notes
POST   /api/grades/grades/           # Créer note
GET    /api/grades/summaries/        # Résumés
GET    /api/grades/summaries/failing_students/  # Échecs
```

### Présences
```
GET    /api/attendance/records/      # Enregistrements
POST   /api/attendance/records/bulk_create/  # Création masse
GET    /api/attendance/summaries/low_attendance/  # Faible présence
```

### Machine Learning
```
GET    /api/ml/models/               # Modèles ML
POST   /api/ml/models/{id}/train/    # Entraîner
POST   /api/ml/models/{id}/activate/ # Activer
```

### Prédictions
```
GET    /api/predictions/predictions/ # Prédictions
GET    /api/predictions/predictions/at_risk/  # À risque
POST   /api/predictions/predictions/generate_bulk/  # Générer
GET    /api/predictions/interventions/  # Interventions
```

### Alertes
```
GET    /api/alerts/alerts/           # Alertes
GET    /api/alerts/alerts/my_alerts/ # Mes alertes
GET    /api/alerts/alerts/critical/  # Critiques
POST   /api/alerts/alerts/{id}/acknowledge/  # Accuser réception
POST   /api/alerts/alerts/{id}/resolve/      # Résoudre
```

### Documentation
```
GET    /api/schema/                  # OpenAPI schema
GET    /api/docs/                    # Swagger UI
GET    /api/redoc/                   # ReDoc
```

---

## Installation & Démarrage

### Prérequis
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Installation

1. **Créer environnement virtuel**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. **Installer dépendances**:
```bash
pip install -r requirements.txt
```

3. **Configurer .env**:
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

4. **Créer base de données**:
```sql
CREATE DATABASE spas_db;
CREATE USER spas_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;
```

5. **Appliquer migrations**:
```bash
python manage.py migrate
```

6. **Créer superuser**:
```bash
python manage.py createsuperuser
```

7. **Créer données de test** (optionnel):
```bash
python manage.py init_spas
python scripts/create_sample_data.py
```

### Démarrage

**Serveur Django**:
```bash
python manage.py runserver
# API disponible sur http://localhost:8000
```

**Celery Worker** (terminal séparé):
```bash
celery -A config worker -l info
```

**Celery Beat** (tâches planifiées, terminal séparé):
```bash
celery -A config beat -l info
```

**Redis** (terminal séparé):
```bash
redis-server
```

---

## Tests

### Lancer tests
```bash
# Tous les tests
python manage.py test

# Tests spécifiques
python manage.py test apps.students
python manage.py test apps.students.tests.StudentModelTest

# Avec pytest
pytest
pytest apps/students/tests.py
pytest -v --cov=apps  # Avec coverage
```

### Structure tests
```python
from django.test import TestCase
from apps.students.models import Student

class StudentModelTest(TestCase):
    def setUp(self):
        # Créer données de test
        pass

    def test_student_creation(self):
        # Test création
        pass
```

---

## Docker

### Démarrage avec Docker

```bash
# Build et démarrer tous les services
docker-compose up -d

# Services:
# - postgres: PostgreSQL sur port 5432
# - redis: Redis sur port 6379
# - backend: Django sur port 8000
# - celery_worker: Worker Celery
# - celery_beat: Beat Celery

# Voir logs
docker-compose logs -f backend

# Arrêter
docker-compose down

# Migrations
docker-compose exec backend python manage.py migrate

# Créer superuser
docker-compose exec backend python manage.py createsuperuser
```

---

## Workflow Développement

### 1. Créer nouvelle feature

```bash
# Créer branche
git checkout -b feature/nouvelle-fonctionnalite

# Développer
# ...

# Tester
python manage.py test

# Commit
git add .
git commit -m "feat: nouvelle fonctionnalité"
```

### 2. Ajouter nouveau modèle

```python
# Dans apps/mon_app/models.py
class MonModele(models.Model):
    # Définir champs
    pass

# Créer migrations
python manage.py makemigrations

# Appliquer
python manage.py migrate
```

### 3. Créer API endpoint

```python
# Serializer
class MonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonModele
        fields = '__all__'

# ViewSet
class MonViewSet(viewsets.ModelViewSet):
    queryset = MonModele.objects.all()
    serializer_class = MonSerializer
    permission_classes = [IsAuthenticated]

# URLs
router.register(r'mon-endpoint', MonViewSet)
```

---

## Performance & Optimisation

### Base de données
- Index sur champs recherchés fréquemment
- `select_related()` pour FK
- `prefetch_related()` pour M2M
- Pagination sur listes longues

### Cache
- Redis pour cache queries fréquentes
- Cache serializers lourds
- Cache sessions

### Requêtes
```python
# Bon - 1 requête
students = Student.objects.select_related('program', 'session').all()

# Mauvais - N+1 queries
students = Student.objects.all()
for s in students:
    print(s.program.name)  # Query pour chaque étudiant!
```

---

## Sécurité

### Checklist Production
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` unique et secret
- [ ] `ALLOWED_HOSTS` configuré
- [ ] HTTPS activé
- [ ] CORS restreint aux domaines légitimes
- [ ] Rate limiting activé
- [ ] Logs de sécurité activés
- [ ] Validation entrées stricte
- [ ] Permissions testées
- [ ] Backups DB automatisés

### Bonnes pratiques
- Ne jamais commit `.env`
- Rotate SECRET_KEY régulièrement
- Valider toutes les entrées utilisateur
- Utiliser parameterized queries (ORM Django)
- Limiter taille uploads
- Sanitize données affichées

---

## Monitoring & Logs

### Logs
```python
import logging
logger = logging.getLogger(__name__)

# Dans views.py
logger.info(f"Student {student.id} created")
logger.error(f"Error processing prediction: {e}")
```

### Fichiers logs
- `logs/spas.log` - Logs application
- `logs/django.log` - Logs Django
- Console - Logs développement

### Métriques à surveiller
- Temps réponse API
- Taux d'erreur
- Utilisation CPU/RAM
- Connexions DB
- Taille queue Celery

---

## Troubleshooting

### Problèmes courants

**Erreur migrations**:
```bash
# Reset migrations (DANGER - perte données!)
python manage.py migrate --fake app_name zero
python manage.py migrate app_name
```

**Celery ne démarre pas**:
```bash
# Vérifier Redis
redis-cli ping

# Vérifier config
python -c "from config import celery"
```

**CORS errors**:
```python
# Vérifier settings.py
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']
```

---

## Roadmap & Améliorations Futures

### Court terme
- [ ] Tests unitaires complets (>80% coverage)
- [ ] Rate limiting (Django REST Framework)
- [ ] Notifications email/push
- [ ] Export données (CSV, Excel)
- [ ] Import bulk étudiants

### Moyen terme
- [ ] Dashboard analytics temps réel
- [ ] Rapports automatisés
- [ ] Intégration systèmes externes (LMS)
- [ ] API versioning (v1, v2)
- [ ] GraphQL endpoint (optionnel)

### Long terme
- [ ] Microservices architecture
- [ ] Event sourcing
- [ ] Scalabilité horizontale
- [ ] Multi-tenancy
- [ ] Mobile app API

---

## Ressources

### Documentation
- [Django 5.0](https://docs.djangoproject.com/en/5.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery](https://docs.celeryproject.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Redis](https://redis.io/documentation)

### Guides internes
- `README.md` - Documentation principale
- `QUICKSTART.md` - Guide démarrage rapide
- `API_GUIDE.md` - Documentation API complète
- `RAPPORT_IMPLEMENTATION_BACKEND.md` - Rapport implémentation détaillé

---

**Dernière mise à jour**: 2026-01-02
**Version Backend**: 1.0.0
**Statut**: Production Ready
