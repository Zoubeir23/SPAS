# Guide de Démarrage Rapide - Authentification SPAS

## Installation Rapide

### 1. Prérequis
```bash
# Vérifier Python 3.11+
python --version

# Vérifier PostgreSQL
psql --version

# Installer et démarrer Redis
# Windows: Télécharger depuis https://redis.io/download
# Linux/Mac:
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Démarrer Redis
redis-server

# Vérifier Redis
redis-cli ping  # Devrait retourner "PONG"
```

### 2. Installation des Dépendances
```bash
cd C:\Users\Public\Libraries\one\SPAS\backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration de la Base de Données
```bash
# Créer la base de données PostgreSQL
psql -U postgres
CREATE DATABASE spas_db;
\q

# Créer le fichier .env
cp .env.example .env  # Si .env.example existe
# Ou créer manuellement
```

### 4. Fichier .env
Créer `C:\Users\Public\Libraries\one\SPAS\backend\.env`:

```env
# Django
DEBUG=True
SECRET_KEY=votre-secret-key-tres-longue-et-securisee-changez-moi
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=spas_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (pour développement)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@spas.com

# Frontend
FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 5. Migrations et Création de Superuser
```bash
# Créer le dossier logs
mkdir logs

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
# Email: admin@spas.com
# Password: AdminSecure123!
```

### 6. Lancer le Serveur
```bash
# Terminal 1: Serveur Django
python manage.py runserver

# Terminal 2 (optionnel): Celery worker
celery -A config worker -l info

# Terminal 3 (optionnel): Redis (si pas déjà démarré)
redis-server
```

## Tests Rapides

### Option 1: Script de Test Automatique
```bash
# Dans le dossier backend
python test_auth.py
```

Ce script teste automatiquement:
- Force de mot de passe
- Inscription
- Vérification d'email
- Connexion
- Requêtes authentifiées
- Rafraîchissement de token
- Protection brute force
- Déconnexion
- Historique d'activité

### Option 2: Tests Manuels avec cURL

#### 1. Vérifier Force de Mot de Passe
```bash
curl -X POST http://localhost:8000/api/auth/password/check-strength/ \
  -H "Content-Type: application/json" \
  -d '{"password":"SecureP@ssw0rd123!"}'
```

#### 2. Inscription
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@spas.com",
    "password": "SecureP@ssw0rd123!",
    "password_confirm": "SecureP@ssw0rd123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "teacher"
  }'
```

**Note**: Copier le `verification_token` de la réponse ou vérifier la console Django.

#### 3. Vérifier Email
```bash
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token":"VOTRE_TOKEN_ICI"}'
```

#### 4. Connexion
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@spas.com",
    "password": "SecureP@ssw0rd123!"
  }'
```

**Note**: Copier l'`access` et le `refresh` token de la réponse.

#### 5. Obtenir les Infos Utilisateur
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN"
```

#### 6. Rafraîchir le Token
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"VOTRE_REFRESH_TOKEN"}'
```

#### 7. Déconnexion
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"VOTRE_REFRESH_TOKEN"}'
```

### Option 3: Interface Swagger

Ouvrir dans le navigateur:
```
http://localhost:8000/api/docs/
```

Interface interactive pour tester tous les endpoints.

## Configuration Email en Production

### Gmail
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_app_password
```

**Important**: Utiliser un "App Password" Gmail, pas votre mot de passe principal.

### SendGrid
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=votre_api_key_sendgrid
```

## Personnalisation

### Modifier les Limites de Rate Limiting

Dans `backend/config/settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/minute',          # Modifier ici
        'register': '5/day',           # Modifier ici
        'password_reset': '5/hour',    # Modifier ici
    }
}
```

### Modifier la Durée de Verrouillage

Dans `backend/apps/authentication/throttling.py`:
```python
class SuspiciousActivityDetector:
    FAILED_LOGIN_THRESHOLD = 5      # Nombre de tentatives
    LOCKOUT_DURATION = 900          # Durée en secondes (15 min)
```

### Modifier les Règles de Mot de Passe

Dans `backend/apps/authentication/utils.py`:
```python
class PasswordValidator:
    MIN_LENGTH = 8                   # Longueur minimum
    REQUIRE_UPPERCASE = True         # Majuscule requise
    REQUIRE_LOWERCASE = True         # Minuscule requise
    REQUIRE_DIGIT = True             # Chiffre requis
    REQUIRE_SPECIAL = True           # Caractère spécial requis
```

### Modifier la Durée de Vie des Tokens

Dans `.env`:
```env
JWT_ACCESS_TOKEN_LIFETIME=30        # minutes
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7   # jours
```

## Endpoints Disponibles

### Inscription et Vérification
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/verify-email/` - Vérifier email
- `POST /api/auth/resend-verification/` - Renvoyer email

### Connexion
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `POST /api/auth/logout-all/` - Déconnexion tous appareils

### Tokens
- `POST /api/auth/token/refresh/` - Rafraîchir token
- `POST /api/auth/token/verify/` - Vérifier token
- `POST /api/auth/token/blacklist-status/` - Statut blacklist

### Mots de Passe
- `POST /api/auth/password/forgot/` - Demander reset
- `POST /api/auth/password/reset/` - Confirmer reset
- `POST /api/auth/password/change/` - Changer mot de passe
- `POST /api/auth/password/check-strength/` - Vérifier force

### Utilisateur
- `GET /api/auth/me/` - Info utilisateur actuel
- `GET /api/auth/activity/` - Historique d'activité

## Dépannage

### Redis ne démarre pas
```bash
# Vérifier le statut
redis-cli ping

# Si erreur de connexion:
# Windows: Vérifier que redis-server.exe est lancé
# Linux: sudo systemctl start redis
# Mac: brew services start redis
```

### Migrations échouent
```bash
# Supprimer toutes les migrations et recommencer
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Emails ne s'envoient pas
```bash
# En développement, utiliser console backend
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Les emails apparaîtront dans la console Django
```

### Erreur "Token blacklisting not enabled"
```bash
# Vérifier que token_blacklist est dans INSTALLED_APPS
# Appliquer les migrations:
python manage.py migrate token_blacklist
```

### Rate limiting ne fonctionne pas
```bash
# Vérifier que Redis est actif
redis-cli ping

# Vérifier la configuration CACHES dans settings.py
# Redémarrer le serveur Django
```

## Prochaines Étapes

1. **Tester tous les endpoints** avec le script ou Swagger
2. **Configurer l'email** pour l'environnement de production
3. **Personnaliser les templates** d'email dans `backend/templates/authentication/emails/`
4. **Ajuster les règles de sécurité** selon vos besoins
5. **Implémenter le frontend** en utilisant les endpoints
6. **Configurer le monitoring** des logs et métriques

## Documentation Complète

- **Documentation API**: http://localhost:8000/api/docs/
- **README du module**: `backend/apps/authentication/README.md`
- **Guide détaillé**: `AUTHENTICATION_IMPROVEMENTS.md`

## Support

Pour toute question:
1. Consulter la documentation Swagger
2. Vérifier les logs dans `backend/logs/spas.log`
3. Examiner le code source commenté
4. Tester avec le script `test_auth.py`

Bonne utilisation du système SPAS!
