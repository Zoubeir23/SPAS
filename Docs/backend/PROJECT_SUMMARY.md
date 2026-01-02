# SPAS Backend - Résumé du Projet

## Vue d'ensemble

Le backend SPAS (Système Prédictif d'Alerte Scolaire) est une API REST Django complète pour la prédiction et la prévention de l'abandon scolaire dans les établissements d'enseignement collégial.

## Architecture Technique

### Stack Technologique
- **Framework**: Django 5.0 + Django REST Framework
- **Base de données**: PostgreSQL 14+
- **Cache/Queue**: Redis 7+
- **Tasks asynchrones**: Celery 5.3
- **Authentification**: JWT (Simple JWT)
- **Documentation API**: drf-spectacular (OpenAPI 3.0)
- **ML**: scikit-learn, pandas, numpy

### Structure du Projet

```
backend/
├── config/                 # Configuration Django
│   ├── __init__.py
│   ├── settings.py        # Settings avec environ
│   ├── urls.py            # URLs principales
│   ├── wsgi.py            # WSGI config
│   ├── celery.py          # Celery config
│   └── exceptions.py      # Gestionnaire d'exceptions personnalisé
│
├── apps/                   # Applications Django
│   ├── users/             # Gestion utilisateurs & auth
│   │   ├── models.py      # User custom model
│   │   ├── serializers.py # UserSerializer, ChangePassword
│   │   ├── views.py       # UserViewSet
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── students/          # Gestion étudiants
│   │   ├── models.py      # Student
│   │   ├── serializers.py
│   │   ├── views.py       # CRUD + at_risk endpoint
│   │   └── management/    # Commandes Django
│   │       └── commands/
│   │           └── init_spas.py  # Initialisation données test
│   │
│   ├── programs/          # Programmes & cours
│   │   ├── models.py      # Program, Course
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── admin.py
│   │
│   ├── sessions/          # Sessions académiques
│   │   ├── models.py      # AcademicPeriod, CourseSession, Enrollment
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── admin.py
│   │
│   ├── grades/            # Notes & évaluations
│   │   ├── models.py      # Grade, CourseGradeSummary
│   │   ├── serializers.py
│   │   ├── views.py       # Statistics, failing_students
│   │   └── admin.py
│   │
│   ├── attendance/        # Présences
│   │   ├── models.py      # AttendanceRecord, AttendanceSummary
│   │   ├── serializers.py
│   │   ├── views.py       # bulk_create, low_attendance
│   │   └── admin.py
│   │
│   ├── ml/                # Machine Learning
│   │   ├── models.py      # MLModel, TrainingJob
│   │   ├── serializers.py
│   │   ├── views.py       # Activation, training
│   │   ├── tasks.py       # train_model_task (Celery)
│   │   └── admin.py
│   │
│   ├── predictions/       # Prédictions & interventions
│   │   ├── models.py      # Prediction, RecommendedIntervention
│   │   ├── serializers.py
│   │   ├── views.py       # at_risk, statistics, generate_bulk
│   │   ├── tasks.py       # generate_predictions_task
│   │   └── admin.py
│   │
│   └── alerts/            # Alertes & actions
│       ├── models.py      # Alert, AlertAction
│       ├── serializers.py
│       ├── views.py       # acknowledge, resolve, assign
│       ├── tasks.py       # create_alerts_from_predictions
│       └── admin.py
│
├── scripts/               # Scripts utilitaires
│   └── create_sample_data.py
│
├── requirements.txt       # Dépendances Python
├── manage.py              # Django management
├── .env.example           # Template variables environnement
├── .gitignore
├── Dockerfile             # Docker config
├── docker-compose.yml     # Services (PostgreSQL, Redis, etc.)
├── pytest.ini             # Configuration tests
├── setup_dev.bat          # Script installation Windows
├── run_dev.bat            # Script démarrage Windows
├── README.md              # Documentation complète
├── QUICKSTART.md          # Guide démarrage rapide
├── API_GUIDE.md           # Documentation API détaillée
└── PROJECT_SUMMARY.md     # Ce fichier
```

## Modèles de Données

### 1. Users (apps.users)
- **User**: Utilisateur custom (email auth)
  - Rôles: ADMIN, TEACHER, ADVISOR, COORDINATOR
  - JWT authentication

### 2. Students (apps.students)
- **Student**: Étudiant
  - Informations personnelles
  - Statut: ACTIVE, INACTIVE, GRADUATED, DROPPED
  - Lien avec Program

### 3. Programs (apps.programs)
- **Program**: Programme d'études
  - Code, nom, durée, crédits requis
- **Course**: Cours
  - Prérequis, crédits, obligatoire/optionnel

### 4. Sessions (apps.sessions)
- **AcademicPeriod**: Période académique (session)
  - Saison: WINTER, SUMMER, FALL
- **CourseSession**: Offre de cours
  - Enseignant, local, horaire, capacité
- **Enrollment**: Inscription étudiant-cours
  - Statut: ENROLLED, DROPPED, COMPLETED

### 5. Grades (apps.grades)
- **Grade**: Note d'évaluation
  - Note (0-100), poids, date
  - Auto-calcul weighted_grade
- **CourseGradeSummary**: Résumé notes cours
  - Note finale, lettre, GPA, réussite
  - Auto-calcul basé sur grades

### 6. Attendance (apps.attendance)
- **AttendanceRecord**: Enregistrement présence
  - Statut: PRESENT, ABSENT, LATE, EXCUSED
- **AttendanceSummary**: Résumé présences
  - Taux présence, compteurs
  - Auto-calcul

### 7. ML (apps.ml)
- **MLModel**: Modèle ML
  - Type, version, métriques (accuracy, precision, etc.)
  - Fichier modèle
- **TrainingJob**: Job entraînement
  - Statut, paramètres, métriques
  - Async avec Celery

### 8. Predictions (apps.predictions)
- **Prediction**: Prédiction risque abandon
  - Score risque (0-100)
  - Niveau: LOW, MEDIUM, HIGH, CRITICAL
  - Facteurs contributifs
  - Confiance
- **RecommendedIntervention**: Intervention recommandée
  - Type, priorité, impact estimé

### 9. Alerts (apps.alerts)
- **Alert**: Alerte
  - Type, sévérité, statut
  - Assignation, résolution
- **AlertAction**: Action sur alerte
  - Type action, description, planification

## Endpoints API Principaux

### Authentification
- `POST /api/auth/token/` - Login (JWT)
- `POST /api/auth/token/refresh/` - Refresh token

### Utilisateurs
- `GET /api/users/me/` - Profil actuel
- `PUT /api/users/update_profile/` - Modifier profil

### Étudiants
- `GET /api/students/` - Liste (filtres: status, program)
- `GET /api/students/at_risk/` - Étudiants à risque

### Prédictions
- `GET /api/predictions/predictions/at_risk/` - Prédictions à risque
- `GET /api/predictions/predictions/statistics/` - Statistiques
- `POST /api/predictions/predictions/generate_bulk/` - Générer prédictions

### Alertes
- `GET /api/alerts/alerts/my_alerts/` - Mes alertes
- `GET /api/alerts/alerts/critical/` - Alertes critiques
- `POST /api/alerts/alerts/{id}/acknowledge/` - Accuser réception
- `POST /api/alerts/alerts/{id}/resolve/` - Résoudre

### Notes & Présences
- `GET /api/grades/summaries/failing_students/` - Étudiants en échec
- `GET /api/attendance/summaries/low_attendance/` - Faible présence

## Fonctionnalités Clés

### 1. Authentification & Permissions
- JWT avec refresh tokens
- Permissions par rôle
- Gestion profils utilisateurs

### 2. Gestion Académique
- Programmes, cours, sessions
- Inscriptions étudiants
- Notes avec auto-calcul
- Présences avec résumés

### 3. Machine Learning
- Entraînement modèles async
- Activation/désactivation modèles
- Métriques performance

### 4. Prédictions
- Génération prédictions en masse
- Scores de risque
- Facteurs contributifs
- Interventions recommandées

### 5. Système d'Alertes
- Alertes automatiques
- Workflow: Active → Acknowledged → Resolved
- Assignation & suivi
- Actions documentées

### 6. Tasks Asynchrones (Celery)
- Entraînement ML
- Génération prédictions
- Création alertes automatiques
- Vérifications périodiques

## Configuration & Déploiement

### Variables Environnement (.env)
```env
DEBUG=True/False
SECRET_KEY=...
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
REDIS_URL
CORS_ALLOWED_ORIGINS
JWT_ACCESS_TOKEN_LIFETIME
```

### Commandes Utiles
```bash
# Installation
python -m venv venv
pip install -r requirements.txt

# Base de données
python manage.py migrate
python manage.py init_spas

# Serveur
python manage.py runserver

# Celery
celery -A config worker -l info

# Tests
python manage.py test
pytest
```

### Docker
```bash
docker-compose up -d  # Démarre PostgreSQL, Redis, backend, Celery
```

## Sécurité

### Implémentées
- JWT authentication
- CORS configuré
- Validation des entrées (serializers)
- Permissions par rôle
- HTTPS en production (settings)
- Secret key management (environ)

### À Implémenter
- Rate limiting (throttling)
- API key pour services externes
- Audit logging
- Data encryption at rest

## Tests & Quality

### Structure Tests
```
apps/{app_name}/tests/
├── test_models.py
├── test_serializers.py
├── test_views.py
└── test_tasks.py
```

### Coverage
- pytest avec coverage
- Configuration dans pytest.ini

## Documentation

### Fichiers
1. **README.md** - Documentation complète
2. **QUICKSTART.md** - Guide démarrage rapide
3. **API_GUIDE.md** - Documentation API détaillée
4. **PROJECT_SUMMARY.md** - Ce résumé

### API Interactive
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Schema OpenAPI: `/api/schema/`

## Données de Test

La commande `python manage.py init_spas` crée:
- 3 utilisateurs (admin, teacher, advisor)
- 1 programme (Techniques informatique)
- 5 cours
- 1 période académique (Automne 2024)
- 8 étudiants avec notes et présences variées
- 1 modèle ML actif

### Credentials
- Admin: admin@spas.ca / admin123
- Teacher: jean.dupont@spas.ca / teacher123
- Advisor: marie.martin@spas.ca / advisor123

## Performance

### Optimisations
- `select_related()` pour relations ForeignKey
- `prefetch_related()` pour relations ManyToMany
- Indexes sur champs fréquemment filtrés
- Pagination (20 items/page)
- Caching avec Redis (à implémenter)

### Async Tasks
- Entraînement ML: Celery worker
- Génération prédictions: Celery worker
- Alertes automatiques: Celery beat (à configurer)

## Évolutions Futures

### Court Terme
1. Rate limiting API
2. Caching Redis
3. Celery beat pour tâches périodiques
4. Tests unitaires complets
5. Monitoring (Sentry, DataDog)

### Moyen Terme
1. Export données (CSV, Excel)
2. Rapports PDF
3. Notifications email/SMS
4. Dashboard analytics
5. Audit logging complet

### Long Terme
1. API GraphQL (optionnel)
2. Webhooks
3. Intégration systèmes externes
4. ML pipeline complet
5. A/B testing interventions

## Contribution

### Standards
- PEP 8 pour Python
- Google docstrings
- Type hints
- Tests pour nouvelles features

### Workflow
1. Branch depuis main
2. Développement + tests
3. Pull request
4. Review + merge

## Licence

Propriétaire - Projet académique SPAS

## Support

Documentation: Voir README.md, QUICKSTART.md, API_GUIDE.md
Issues: Créer un ticket avec description détaillée
Contact: support@spas.ca (fictif)

---

**Version**: 1.0.0
**Date**: 2024-01-01
**Auteur**: Équipe SPAS
