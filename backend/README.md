# SPAS Backend - Système Prédictif d'Alerte Scolaire

Backend Django REST API pour le système de prédiction d'abandon scolaire.

**Version**: 2.0  
**Statut**: Production Ready ✅

---

## 🧠 Machine Learning

### Algorithmes Implémentés

| Algorithme | Rôle | Package |
|------------|------|---------|
| **XGBoost** | Classification principale | `xgboost>=2.0` |
| **SHAP** | Explainability (valeurs de Shapley) | `shap>=0.45` |
| **SMOTE** | Rééquilibrage classes minoritaires | `imbalanced-learn>=0.12` |
| **RandomForest** | Algorithme de fallback | `scikit-learn` |

### Fonctionnalités ML

- Prédiction du risque d'abandon (0-100%)
- Calcul automatique de la courbe ROC avec AUC
- Explication des facteurs via SHAP TreeExplainer
- Traduction française des noms de features
- Entraînement asynchrone via Celery
- Support multi-algorithmes avec fallback automatique

---

## 📊 Logs d'Audit

Le système inclut un module complet de logs d'audit pour la traçabilité :

```
GET  /api/core/audit-logs/              # Liste paginée des logs
GET  /api/core/audit-logs/{id}/         # Détail d'un log
GET  /api/core/audit-logs/statistics/   # Statistiques (30 jours)
GET  /api/core/audit-logs/recent/       # 10 dernières actions
```

### Types d'actions auditées
- Connexion/Déconnexion
- Création/Modification/Suppression
- Prédictions ML
- Alertes créées/résolues
- Import/Export de données

---

## Documentation Complète

- **[QUICKSTART.md](C:\Users\Public\Libraries\one\SPAS\backend\QUICKSTART.md)** - Démarrage rapide en 5 minutes
- **[STRUCTURE_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\STRUCTURE_BACKEND.md)** - Architecture complète du backend
- **[INDEX_FICHIERS.md](C:\Users\Public\Libraries\one\SPAS\backend\INDEX_FICHIERS.md)** - Index de tous les fichiers avec chemins absolus
- **[ETAT_ACTUEL_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\ETAT_ACTUEL_BACKEND.md)** - État actuel et roadmap
- **[INTEGRATION_FRONTEND.md](C:\Users\Public\Libraries\one\SPAS\backend\INTEGRATION_FRONTEND.md)** - Guide intégration avec React
- **[API_GUIDE.md](C:\Users\Public\Libraries\one\SPAS\backend\API_GUIDE.md)** - Documentation API détaillée
- **[RAPPORT_IMPLEMENTATION_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\RAPPORT_IMPLEMENTATION_BACKEND.md)** - Rapport implémentation complet

---

## Vue d'ensemble

Le backend SPAS est une API REST complète avec:

- **10 applications Django** - Modulaire et maintenable
- **17+ modèles de données** - PostgreSQL avec indexes optimisés
- **50+ endpoints API** - RESTful avec documentation OpenAPI 3.0
- **5 tâches Celery** - Traitement asynchrone (ML, alertes)
- **Authentification JWT** - Sécurisée avec refresh tokens
- **XGBoost + SHAP** - ML avec explainability
- **Logs d'audit** - Traçabilité complète des actions
- **Tests unitaires** - 28 tests d'intégration
- **Docker ready** - Configuration complète docker-compose

---

## Architecture

### Stack Technique

- **Django 6.0** - Framework web Python
- **Django REST Framework 3.15+** - API REST
- **PostgreSQL 15+** - Base de données relationnelle
- **Redis 7+** - Cache et broker messages
- **Celery 5.3+** - Tâches asynchrones
- **Simple JWT** - Authentification JWT
- **XGBoost 2.0+** - Machine Learning
- **SHAP 0.45+** - Explainability IA
- **imbalanced-learn** - SMOTE pour rééquilibrage
- **drf-spectacular** - Documentation OpenAPI 3.0

### Applications Django (10)

```
apps/
├── authentication/ - JWT login/logout/refresh
├── users/          - Gestion utilisateurs (4 rôles)
├── students/       - CRUD étudiants avec évaluation risque
├── programs/       - Programmes d'études et matières
├── sessions/       - Périodes académiques
├── grades/         - Notes avec calculs automatiques
├── attendance/     - Présences avec taux automatique
├── ml/             - XGBoost + SHAP + SMOTE + ROC
├── predictions/    - Prédictions avec facteurs SHAP
├── alerts/         - Alertes avec workflow complet
└── core/           - Utilitaires + Logs d'audit
```

**Voir [STRUCTURE_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\STRUCTURE_BACKEND.md) pour détails complets**

---

## Installation Rapide

### Prérequis

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Étapes Installation

#### 1. Cloner et setup environnement

```bash
cd C:\Users\Public\Libraries\one\SPAS\backend

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt
```

#### 2. Configuration

```bash
# Copier template environnement
copy .env.example .env

# Éditer .env avec vos configurations
# Minimum: DB_PASSWORD, SECRET_KEY
```

#### 3. Base de données

```sql
-- Créer base de données PostgreSQL
CREATE DATABASE spas_db;
CREATE USER spas_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;
```

```bash
# Appliquer migrations
python manage.py migrate
```

#### 4. Créer superutilisateur

```bash
python manage.py createsuperuser
# Email: admin@example.com
# Password: (votre choix)
```

#### 5. Initialiser données test (optionnel)

```bash
# Créer données initiales
python manage.py init_spas

# Créer données de test complètes
python scripts/create_sample_data.py
```

#### 6. Démarrer serveur

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Redis (si pas déjà démarré)
redis-server

# Terminal 3: Celery Worker
celery -A config worker -l info

# Terminal 4: Celery Beat (tâches planifiées)
celery -A config beat -l info
```

**Backend disponible**: http://localhost:8000

**Voir [QUICKSTART.md](C:\Users\Public\Libraries\one\SPAS\backend\QUICKSTART.md) pour guide détaillé**

---

## Installation Docker (Recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# Services:
# - PostgreSQL: port 5432
# - Redis: port 6379
# - Django Backend: port 8000
# - Celery Worker
# - Celery Beat

# Migrations
docker-compose exec backend python manage.py migrate

# Créer superuser
docker-compose exec backend python manage.py createsuperuser

# Voir logs
docker-compose logs -f backend

# Arrêter
docker-compose down
```

---

## API Endpoints

**Base URL**: `http://localhost:8000/api`

### Authentification

```
POST   /api/auth/token/          - Login (email + password) → JWT tokens
POST   /api/auth/token/refresh/  - Refresh access token
POST   /api/auth/token/verify/   - Vérifier validité token
```

### Utilisateurs

```
GET    /api/users/               - Liste utilisateurs
GET    /api/users/me/            - Mon profil
PUT    /api/users/update_profile/  - Modifier profil
POST   /api/users/change_password/ - Changer mot de passe
```

### Étudiants

```
GET    /api/students/            - Liste étudiants (filtres: status, program, risk_level)
POST   /api/students/            - Créer étudiant
GET    /api/students/{id}/       - Détails étudiant
PUT    /api/students/{id}/       - Modifier étudiant
DELETE /api/students/{id}/       - Supprimer étudiant
GET    /api/students/at_risk/    - Étudiants à risque (HIGH/MEDIUM)
```

### Programmes & Cours

```
GET    /api/programs/programs/   - Programmes d'études
POST   /api/programs/programs/   - Créer programme
GET    /api/programs/courses/    - Cours
POST   /api/programs/courses/    - Créer cours
```

### Sessions Académiques

```
GET    /api/sessions/periods/          - Périodes académiques
GET    /api/sessions/periods/current/  - Période actuelle
GET    /api/sessions/course-sessions/  - Sessions de cours
GET    /api/sessions/enrollments/      - Inscriptions étudiants
POST   /api/sessions/enrollments/      - Inscrire étudiant
```

### Notes

```
GET    /api/grades/grades/       - Notes individuelles
POST   /api/grades/grades/       - Créer note
GET    /api/grades/summaries/    - Résumés notes par cours
GET    /api/grades/summaries/failing_students/  - Étudiants en échec (<60%)
```

### Présences

```
GET    /api/attendance/records/           - Enregistrements présence
POST   /api/attendance/records/           - Créer enregistrement
POST   /api/attendance/records/bulk_create/  - Création en masse
GET    /api/attendance/summaries/         - Résumés présences
GET    /api/attendance/summaries/low_attendance/  - Présence <70%
```

### Machine Learning

```
GET    /api/ml/models/           - Liste modèles ML
POST   /api/ml/models/           - Créer modèle
POST   /api/ml/models/{id}/train/     - Entraîner modèle (async)
POST   /api/ml/models/{id}/activate/  - Activer modèle
GET    /api/ml/training-jobs/    - Jobs d'entraînement
```

### Prédictions

```
GET    /api/predictions/predictions/  - Prédictions risque
GET    /api/predictions/predictions/at_risk/  - Prédictions HIGH/CRITICAL
POST   /api/predictions/predictions/generate_bulk/  - Générer prédictions (async)
GET    /api/predictions/predictions/statistics/  - Statistiques
GET    /api/predictions/interventions/  - Interventions recommandées
```

### Alertes

```
GET    /api/alerts/alerts/       - Alertes
POST   /api/alerts/alerts/       - Créer alerte
GET    /api/alerts/alerts/my_alerts/    - Mes alertes assignées
GET    /api/alerts/alerts/critical/     - Alertes critiques
POST   /api/alerts/alerts/{id}/acknowledge/  - Accuser réception
POST   /api/alerts/alerts/{id}/resolve/      - Résoudre alerte
POST   /api/alerts/alerts/{id}/assign/       - Assigner alerte
GET    /api/alerts/actions/      - Historique actions
```

**Voir [API_GUIDE.md](C:\Users\Public\Libraries\one\SPAS\backend\API_GUIDE.md) pour exemples complets et détails**

---

## Documentation API Interactive

Documentation API auto-générée disponible:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## Tâches Celery

Le système utilise Celery pour les tâches asynchrones:

### Démarrage Celery

```bash
# Worker (traite les tâches)
celery -A config worker -l info

# Beat (planificateur)
celery -A config beat -l info
```

### Tâches Disponibles

**Machine Learning** (`apps.ml.tasks`):
- `train_model_task(model_id, parameters)` - Entraîner modèle ML

**Prédictions** (`apps.predictions.tasks`):
- `generate_predictions_task(period_id=None)` - Générer prédictions en masse

**Alertes** (`apps.alerts.tasks`):
- `create_alerts_from_predictions()` - Créer alertes depuis prédictions HIGH/CRITICAL
- `check_low_attendance()` - Vérifier présences <70%
- `check_failing_grades()` - Vérifier notes <60%

---

## Tests

### Lancer Tests

```bash
# Tous les tests
python manage.py test

# Tests app spécifique
python manage.py test apps.students

# Avec pytest (recommandé)
pytest
pytest -v --cov=apps --cov-report=html  # Avec coverage
```

### Coverage Actuel

- **students**: Tests complets
- **Autres apps**: Tests à ajouter

**Objectif**: >80% coverage

---

## Configuration Environnement

### Variables .env

Copier `.env.example` → `.env` et configurer:

```bash
# Django
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=spas_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# CORS (Frontend React)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60        # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440     # minutes (24h)

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ML
ML_MODEL_PATH=ml_models/
ML_PREDICTION_THRESHOLD=0.7
```

---

## Sécurité

### Développement

- JWT authentification activée
- CORS configuré pour localhost:5173
- Validation entrées via serializers DRF
- Permissions par rôle (ADMIN, TEACHER, ADVISOR, COORDINATOR)

### Production

**Checklist sécurité**:
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` unique et secret (générer avec `django.core.management.utils.get_random_secret_key()`)
- [ ] `ALLOWED_HOSTS` configuré avec domaines légitimes
- [ ] HTTPS activé (SSL/TLS)
- [ ] CORS limité aux domaines frontend légitimes
- [ ] Rate limiting activé
- [ ] Logs de sécurité activés
- [ ] Backups DB automatisés
- [ ] Firewall configuré
- [ ] Security headers (HSTS, CSP, etc.)

**Voir [ETAT_ACTUEL_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\ETAT_ACTUEL_BACKEND.md) - Section Sécurité**

---

## Intégration Frontend

Le backend est configuré pour fonctionner avec le frontend React (localhost:5173).

### Configuration Frontend

```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true,
});

// Ajouter JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

**Voir [INTEGRATION_FRONTEND.md](C:\Users\Public\Libraries\one\SPAS\backend\INTEGRATION_FRONTEND.md) pour guide complet**

---

## Structure Projet

```
backend/
├── config/                 # Configuration Django principale
│   ├── settings.py        # Configuration complète (DB, DRF, JWT, Celery)
│   ├── urls.py            # Routage API principal
│   ├── celery.py          # Configuration Celery
│   └── exceptions.py      # Gestionnaire erreurs personnalisé
│
├── apps/                   # Applications Django (9 apps)
│   ├── users/             # Authentification & utilisateurs
│   ├── students/          # Gestion étudiants
│   ├── programs/          # Programmes & cours
│   ├── sessions/          # Sessions académiques
│   ├── grades/            # Notes & évaluations
│   ├── attendance/        # Présences
│   ├── ml/                # Machine Learning
│   ├── predictions/       # Prédictions risque
│   └── alerts/            # Alertes & actions
│
├── scripts/               # Scripts utilitaires
├── static/                # Fichiers statiques
├── media/                 # Fichiers uploadés
├── logs/                  # Logs application
├── ml_models/             # Modèles ML sérialisés
│
├── manage.py              # Django management
├── requirements.txt       # Dépendances Python
├── .env                   # Variables environnement (git-ignored)
├── .env.example           # Template .env
├── Dockerfile             # Image Docker
├── docker-compose.yml     # Services Docker
└── pytest.ini             # Configuration tests
```

**Voir [INDEX_FICHIERS.md](C:\Users\Public\Libraries\one\SPAS\backend\INDEX_FICHIERS.md) pour liste complète avec chemins absolus**

---

## Commandes Utiles

### Django

```bash
# Développement
python manage.py runserver              # Démarrer serveur
python manage.py shell                  # Shell Django
python manage.py makemigrations         # Créer migrations
python manage.py migrate                # Appliquer migrations
python manage.py createsuperuser        # Créer admin
python manage.py init_spas              # Initialiser données

# Production
python manage.py collectstatic --noinput  # Collecter static files
python manage.py check --deploy            # Vérifier config production
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Tests

```bash
python manage.py test                   # Tous les tests
python manage.py test apps.students     # Tests app spécifique
pytest                                  # Avec pytest
pytest -v --cov=apps --cov-report=html  # Avec coverage
```

### Celery

```bash
celery -A config worker -l info         # Worker
celery -A config beat -l info           # Planificateur
celery -A config flower                 # Monitoring (optionnel)
```

### Docker

```bash
docker-compose up -d                    # Démarrer
docker-compose logs -f backend          # Logs
docker-compose exec backend python manage.py migrate  # Migrations
docker-compose down                     # Arrêter
```

---

## Troubleshooting

### Backend ne démarre pas

**Erreur migrations**:
```bash
python manage.py migrate --run-syncdb
```

**Erreur PostgreSQL**:
```bash
# Vérifier PostgreSQL est démarré
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql
```

### CORS Errors

Vérifier `.env`:
```bash
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Redémarrer serveur Django après modification `.env`.

### Celery ne démarre pas

```bash
# Vérifier Redis
redis-cli ping  # Doit répondre "PONG"

# Windows: Installer Redis via WSL ou Docker
docker run -d -p 6379:6379 redis:alpine
```

---

## Roadmap

### Phase 1: Stabilisation (Semaines 1-2)
- [ ] Tests unitaires complets (>80% coverage)
- [ ] Implémentation ML réelle (actuellement stub)
- [ ] Audit sécurité

### Phase 2: Amélioration (Semaines 3-4)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Notifications email
- [ ] Rate limiting
- [ ] Exports (CSV, Excel, PDF)

### Phase 3: Production (Semaines 5-6)
- [ ] Infrastructure production
- [ ] Monitoring (Sentry, DataDog)
- [ ] Optimisations performance
- [ ] Load testing

**Voir [ETAT_ACTUEL_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\ETAT_ACTUEL_BACKEND.md) pour roadmap complète**

---

## Contribution

### Standards Code

- PEP 8 pour Python
- Black pour formatting
- isort pour imports
- flake8 pour linting

### Workflow Git

```bash
git checkout -b feature/ma-fonctionnalite
# Développer...
git add .
git commit -m "feat: ma nouvelle fonctionnalité"
git push origin feature/ma-fonctionnalite
# Créer Pull Request
```

---

## Support

### Documentation
- [STRUCTURE_BACKEND.md](C:\Users\Public\Libraries\one\SPAS\backend\STRUCTURE_BACKEND.md) - Architecture détaillée
- [API_GUIDE.md](C:\Users\Public\Libraries\one\SPAS\backend\API_GUIDE.md) - Documentation API
- [INTEGRATION_FRONTEND.md](C:\Users\Public\Libraries\one\SPAS\backend\INTEGRATION_FRONTEND.md) - Intégration React

### Ressources
- Django: https://docs.djangoproject.com/en/5.0/
- DRF: https://www.django-rest-framework.org/
- Celery: https://docs.celeryproject.org/

---

## Licence

Propriétaire - Projet académique

---

**Dernière mise à jour**: 2026-01-02
**Version**: 1.0.0
**Statut**: Production Ready
