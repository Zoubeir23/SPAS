# SPAS — Système Prédictif d'Alerte Scolaire

Plateforme académique Django/React qui utilise le machine learning (XGBoost + SHAP) pour identifier les étudiants à risque d'abandon scolaire et déclencher des alertes proactives.

## Fonctionnalités

| Domaine | Détail |
|---|---|
| **Authentification** | JWT avec refresh tokens, contrôle d'accès par rôle (RBAC) |
| **Gestion académique** | Étudiants, programmes, sessions, notes, absences |
| **Prédictions ML** | Score de risque 0-100 %, facteurs explicatifs SHAP, courbe ROC interactive |
| **Alertes** | Déclenchement automatique, interventions pédagogiques, workflow de résolution |
| **Rôles** | Admin · Enseignant · Conseiller pédagogique · Data Scientist |

---

## Démarrage rapide

### Option 1 — Docker (recommandé)

```bash
git clone https://github.com/Zoubeir23/SPAS.git
cd SPAS/backend

# Copier et adapter la configuration
cp .env.example .env
# Éditer .env si nécessaire (les valeurs par défaut fonctionnent avec Docker)

# Lancer PostgreSQL + Redis + Django + Celery
docker compose up -d

# Créer les tables et charger les données de démonstration
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py init_spas
```

API disponible sur **http://localhost:8000**  
Swagger UI : **http://localhost:8000/api/docs/**

Lancer ensuite le frontend :
```bash
cd ../frontend
npm install
npm run dev
# http://localhost:5173
```

### Option 2 — Installation locale

**Prérequis :** Python 3.10+, Node 18+, PostgreSQL 15+, Redis 7+

```bash
git clone https://github.com/Zoubeir23/SPAS.git
cd SPAS/backend

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos identifiants PostgreSQL

# Installer les dépendances Python
python -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

pip install -r requirements.txt

# Initialiser la base de données
python manage.py migrate
python manage.py init_spas        # Données de démonstration

# Démarrer le serveur
python manage.py runserver
```

```bash
# Dans un autre terminal — worker Celery (tâches ML asynchrones)
source venv/bin/activate
celery -A config worker -l info
```

```bash
# Frontend
cd ../frontend
npm install
npm run dev
```

---

## Configuration (.env)

Copier `backend/.env.example` vers `backend/.env` et adapter les valeurs :

| Variable | Description | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django — **changer en production** | — |
| `DEBUG` | Mode debug | `True` |
| `DB_NAME` | Nom de la base PostgreSQL | `spas_db` |
| `DB_USER` | Utilisateur PostgreSQL | `spas_user` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | — |
| `DB_HOST` | Hôte PostgreSQL | `localhost` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379/0` |
| `JWT_ACCESS_TOKEN_LIFETIME` | Durée du token d'accès (minutes) | `60` |
| `CORS_ALLOWED_ORIGINS` | Origines frontend autorisées | `http://localhost:5173` |

---

## Tests

```bash
cd backend

# Tests complets avec couverture
pytest --cov=apps --cov-report=html

# Tests de sécurité uniquement (pas besoin de PostgreSQL)
DJANGO_SETTINGS_MODULE=config.settings_test \
DB_PASSWORD=test DB_NAME=test DB_USER=test \
pytest tests/test_security_permissions.py -v
```

La suite couvre : authentification, contrôle d'accès RBAC, protection IDOR, prédictions ML, alertes.

---

## Structure du projet

```
SPAS/
├── backend/
│   ├── apps/
│   │   ├── authentication/   # JWT, inscription, vérification email
│   │   ├── users/            # Modèle utilisateur, rôles
│   │   ├── students/         # Gestion des étudiants
│   │   ├── programs/         # Programmes et matières
│   │   ├── sessions/         # Sessions académiques
│   │   ├── grades/           # Notes
│   │   ├── attendance/       # Absences
│   │   ├── predictions/      # Prédictions ML (XGBoost)
│   │   ├── alerts/           # Alertes et interventions
│   │   ├── ml/               # Entraînement, modèles, SHAP
│   │   └── core/             # Permissions, mixins, utilitaires
│   ├── config/               # Settings Django, URLs, WSGI
│   └── tests/                # Suite de tests (pytest)
└── frontend/
    ├── src/pages/            # 18 pages React
    ├── src/components/       # Composants réutilisables
    ├── src/api/              # Clients API (Axios)
    ├── src/hooks/            # Hooks personnalisés
    └── src/store/            # État global (Zustand)
```

---

## Comptes de démonstration

> Disponibles après `python manage.py init_spas`

| Email | Rôle | Mot de passe |
|---|---|---|
| admin@isi.edu | Administrateur | Voir `.env` / `init_spas` |
| teacher@isi.edu | Enseignant | Voir `.env` / `init_spas` |
| ds@isi.edu | Data Scientist | Voir `.env` / `init_spas` |
| pedagogical@isi.edu | Conseiller pédagogique | Voir `.env` / `init_spas` |

---

## Technologies

**Backend :** Django 6 · Django REST Framework · PostgreSQL 15 · Simple JWT · Celery · Redis · XGBoost · SHAP · imbalanced-learn (SMOTE)

**Frontend :** React 18 · TypeScript · Vite · Tailwind CSS · Zustand · Recharts · React Router 7

**Infrastructure :** Docker · GitHub Actions CI · pytest · GitGuardian

---

## Contribuer

```bash
# Créer une branche de feature
git checkout -b feat/ma-fonctionnalite

# Lancer les tests avant de pousser
cd backend && pytest --no-cov -q

# Ouvrir une Pull Request vers main
```

Le CI vérifie automatiquement : tests Django, build TypeScript, audit de sécurité GitGuardian.

---

**Auteur :** Zoubeir IBRAHIMA AMED  
**Contexte :** Mémoire de fin d'études  
**Licence :** MIT
