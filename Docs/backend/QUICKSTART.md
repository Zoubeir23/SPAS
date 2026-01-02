# SPAS Backend - Guide de Démarrage Rapide

## Installation Rapide (Windows)

### 1. Prérequis
- Python 3.11 ou supérieur
- PostgreSQL 14 ou supérieur
- Redis 7 (optionnel pour développement)

### 2. Configuration Automatique

Exécutez le script de configuration:
```bash
setup_dev.bat
```

Ce script va:
- Créer un environnement virtuel
- Installer toutes les dépendances
- Créer le fichier .env
- Créer les dossiers nécessaires

### 3. Configuration PostgreSQL

Créez la base de données:
```sql
-- Connectez-vous à PostgreSQL
psql -U postgres

-- Créez la base de données et l'utilisateur
CREATE DATABASE spas_db;
CREATE USER spas_user WITH PASSWORD 'spas_password';
GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;
```

### 4. Configuration .env

Modifiez le fichier `.env` avec vos paramètres:
```env
DEBUG=True
SECRET_KEY=votre-cle-secrete-unique-ici
DB_NAME=spas_db
DB_USER=spas_user
DB_PASSWORD=spas_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Initialisation de la Base de Données

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Appliquer les migrations
python manage.py migrate

# Créer les données de test
python manage.py init_spas

# OU créer seulement un superutilisateur
python manage.py createsuperuser
```

### 6. Démarrage du Serveur

Option 1 - Script automatique:
```bash
run_dev.bat
```

Option 2 - Manuel:
```bash
venv\Scripts\activate
python manage.py runserver
```

Le serveur démarre sur: http://localhost:8000

## Accès aux Interfaces

### Admin Django
- URL: http://localhost:8000/admin/
- Identifiants: admin@spas.ca / admin123

### API Documentation
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema OpenAPI: http://localhost:8000/api/schema/

### API REST
- Base URL: http://localhost:8000/api/

## Test de l'API

### 1. Obtenir un Token JWT

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@spas.ca\",\"password\":\"admin123\"}"
```

Réponse:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

### 2. Utiliser le Token

```bash
curl http://localhost:8000/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Endpoints Principaux

### Authentification
- `POST /api/auth/token/` - Obtenir token
- `POST /api/auth/token/refresh/` - Rafraîchir token

### Utilisateurs
- `GET /api/users/` - Liste utilisateurs
- `GET /api/users/me/` - Profil actuel

### Étudiants
- `GET /api/students/` - Liste étudiants
- `POST /api/students/` - Créer étudiant
- `GET /api/students/{id}/` - Détails étudiant
- `GET /api/students/at_risk/` - Étudiants à risque

### Prédictions
- `GET /api/predictions/predictions/` - Prédictions
- `GET /api/predictions/predictions/at_risk/` - À risque
- `GET /api/predictions/predictions/statistics/` - Statistiques

### Alertes
- `GET /api/alerts/alerts/` - Alertes
- `GET /api/alerts/alerts/my_alerts/` - Mes alertes
- `GET /api/alerts/alerts/critical/` - Alertes critiques

## Développement avec Docker (Optionnel)

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f backend

# Arrêter les services
docker-compose down
```

## Données de Test

Après `python manage.py init_spas`, vous aurez:

**Utilisateurs:**
- Admin: admin@spas.ca / admin123
- Enseignant: jean.dupont@spas.ca / teacher123
- Conseiller: marie.martin@spas.ca / advisor123

**Étudiants:**
- 8 étudiants avec notes et présences variées
- 3 cours par étudiant
- Notes de 55% à 92%
- Taux de présence variés

**Structure:**
- 1 programme (Techniques de l'informatique)
- 5 cours
- 1 période académique (Automne 2024)
- 5 sessions de cours
- 24 inscriptions
- Plusieurs notes et présences

## Tâches Celery (Optionnel)

Pour les fonctionnalités ML asynchrones:

```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - Celery Worker
celery -A config worker -l info

# Terminal 3 - Django Server
python manage.py runserver
```

## Commandes Utiles

```bash
# Créer une nouvelle migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Collecter les fichiers statiques
python manage.py collectstatic

# Réinitialiser les données de test
python manage.py init_spas --clear
```

## Dépannage

### Erreur de connexion PostgreSQL
- Vérifiez que PostgreSQL est démarré
- Vérifiez les paramètres dans .env
- Testez la connexion: `psql -U spas_user -d spas_db`

### Erreur "No module named..."
```bash
pip install -r requirements.txt
```

### Erreur de migration
```bash
python manage.py migrate --run-syncdb
```

### Port 8000 déjà utilisé
```bash
python manage.py runserver 8001
```

## Prochaines Étapes

1. Explorez l'API avec Swagger: http://localhost:8000/api/docs/
2. Testez les endpoints avec Postman ou curl
3. Consultez la documentation complète dans README.md
4. Développez votre frontend React pour consommer l'API

## Support

Pour toute question ou problème:
- Consultez README.md pour la documentation complète
- Vérifiez les logs: `backend/logs/spas.log`
- Examinez le panneau d'administration Django
