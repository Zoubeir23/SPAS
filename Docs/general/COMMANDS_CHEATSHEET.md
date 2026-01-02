# Aide-Mémoire des Commandes - SPAS Authentication

## Installation et Configuration

### Installation Initiale
```bash
# Cloner le projet
cd C:\Users\Public\Libraries\one\SPAS\backend

# Créer environnement virtuel
python -m venv venv

# Activer environnement (Windows)
venv\Scripts\activate

# Activer environnement (Linux/Mac)
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Créer fichier .env
cp .env.example .env
# Puis éditer .env avec vos valeurs
```

### Configuration Base de Données
```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer base de données
CREATE DATABASE spas_db;
CREATE USER spas_user WITH PASSWORD 'votre_password';
GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;
\q

# Appliquer migrations
python manage.py makemigrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser
```

### Configuration Redis
```bash
# Installer Redis (Windows - via WSL ou Windows port)
# Télécharger depuis: https://github.com/microsoftarchive/redis/releases

# Installer Redis (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install redis-server

# Installer Redis (macOS)
brew install redis

# Démarrer Redis
redis-server

# Vérifier Redis
redis-cli ping  # Doit retourner PONG

# Se connecter à Redis
redis-cli

# Commandes Redis utiles
PING                    # Tester connexion
KEYS spas:*            # Voir toutes les clés SPAS
GET spas:key           # Voir valeur d'une clé
FLUSHDB                # Vider base de données Redis (attention!)
```

## Développement

### Serveur de Développement
```bash
# Lancer serveur Django
python manage.py runserver

# Lancer sur port spécifique
python manage.py runserver 8080

# Lancer sur toutes les interfaces
python manage.py runserver 0.0.0.0:8000
```

### Celery (Tâches Asynchrones)
```bash
# Lancer worker Celery
celery -A config worker -l info

# Lancer beat (tâches planifiées)
celery -A config beat -l info

# Lancer worker et beat ensemble
celery -A config worker -B -l info

# Voir tâches actives
celery -A config inspect active

# Purger toutes les tâches
celery -A config purge
```

### Migrations
```bash
# Créer nouvelles migrations
python manage.py makemigrations

# Créer migration pour une app spécifique
python manage.py makemigrations authentication

# Voir SQL généré
python manage.py sqlmigrate authentication 0001

# Appliquer migrations
python manage.py migrate

# Annuler migrations (revenir à version)
python manage.py migrate authentication 0001

# Voir statut migrations
python manage.py showmigrations

# Voir plan de migration
python manage.py migrate --plan
```

### Shell Django
```bash
# Shell Django
python manage.py shell

# Shell avec IPython (si installé)
python manage.py shell -i ipython

# Exemples dans le shell:
from apps.users.models import User
from apps.authentication.utils import PasswordValidator

# Créer utilisateur
user = User.objects.create_user(
    email='test@spas.com',
    password='SecurePass123!',
    first_name='Test',
    last_name='User',
    role='teacher'
)

# Vérifier force mot de passe
is_valid, errors = PasswordValidator.validate_password_strength('Test123!')

# Obtenir tous les utilisateurs
users = User.objects.all()

# Activer tous les utilisateurs inactifs
User.objects.filter(is_active=False).update(is_active=True)
```

## Tests

### Tests Automatisés
```bash
# Tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test apps.authentication

# Tests avec verbose
python manage.py test --verbosity=2

# Tests avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère rapport HTML dans htmlcov/
```

### Script de Test Custom
```bash
# Test complet du système auth
python test_auth.py

# Avec sortie détaillée
python test_auth.py -v
```

### Tests Manuel avec cURL
```bash
# Test inscription
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecureP@ss123!",
    "password_confirm": "SecureP@ss123!",
    "first_name": "Test",
    "last_name": "User",
    "role": "teacher"
  }'

# Test connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecureP@ss123!"
  }'

# Test endpoint authentifié
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN"

# Test refresh token
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"VOTRE_REFRESH_TOKEN"}'
```

## Gestion des Utilisateurs

### Commandes Django
```bash
# Créer superuser
python manage.py createsuperuser

# Changer mot de passe utilisateur
python manage.py changepassword email@example.com

# Créer utilisateur custom
python manage.py shell
>>> from apps.users.models import User
>>> user = User.objects.create_user(
...     email='user@spas.com',
...     password='SecurePass123!',
...     first_name='John',
...     last_name='Doe',
...     role='teacher'
... )
>>> user.is_active = True
>>> user.save()
```

### Gestion en Base
```bash
# Via psql
psql -U postgres -d spas_db

# Voir tous les utilisateurs
SELECT id, email, first_name, last_name, role, is_active FROM users;

# Activer un utilisateur
UPDATE users SET is_active = TRUE WHERE email = 'user@spas.com';

# Voir tokens JWT actifs
SELECT * FROM token_blacklist_outstandingtoken ORDER BY created_at DESC LIMIT 10;

# Voir tokens blacklistés
SELECT * FROM token_blacklist_blacklistedtoken ORDER BY blacklisted_at DESC LIMIT 10;
```

## Monitoring et Logs

### Logs
```bash
# Voir logs en temps réel
tail -f logs/spas.log

# Voir dernières 100 lignes
tail -n 100 logs/spas.log

# Chercher erreurs
grep ERROR logs/spas.log

# Chercher par utilisateur
grep "user@spas.com" logs/spas.log

# Chercher tentatives connexion échouées
grep "Failed login" logs/spas.log
```

### Redis Monitoring
```bash
# Connexion Redis CLI
redis-cli

# Voir statistiques
INFO stats

# Voir mémoire utilisée
INFO memory

# Voir toutes les clés auth
KEYS spas:auth_events_*

# Voir événements utilisateur
GET spas:auth_events_user@spas.com

# Voir tentatives login échouées
KEYS spas:suspicious_login_*

# Voir comptes verrouillés
KEYS spas:lockout_*

# Effacer verrouillage manuel
DEL spas:lockout_user@spas.com
DEL spas:suspicious_login_user@spas.com
```

### Base de Données
```bash
# Connexions actives
SELECT count(*) FROM pg_stat_activity;

# Queries lentes
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '5 seconds';

# Taille de la DB
SELECT pg_size_pretty(pg_database_size('spas_db'));

# Taille des tables
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Maintenance

### Nettoyage
```bash
# Nettoyer tokens JWT expirés
python manage.py flushexpiredtokens

# Nettoyer sessions expirées
python manage.py clearsessions

# Nettoyer cache Redis
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Ou via Redis CLI
redis-cli FLUSHDB
```

### Backup
```bash
# Backup PostgreSQL
pg_dump -U postgres spas_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup avec compression
pg_dump -U postgres spas_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restaurer backup
psql -U postgres spas_db < backup_20260102_120000.sql

# Backup Redis
redis-cli SAVE
# Fichier sauvegardé dans dump.rdb

# Copier backup Redis
cp /var/lib/redis/dump.rdb /path/to/backup/dump_$(date +%Y%m%d).rdb
```

### Mise à Jour
```bash
# Mettre à jour dépendances
pip list --outdated

# Mettre à jour package spécifique
pip install -U package-name

# Mettre à jour requirements.txt
pip freeze > requirements.txt

# Vérifier vulnérabilités
pip install safety
safety check

# Mettre à jour Django
pip install -U Django
python manage.py migrate
```

## Production

### Collecte Fichiers Statiques
```bash
# Collecter fichiers statiques
python manage.py collectstatic --noinput

# Avec verbose
python manage.py collectstatic --noinput --verbosity=2

# Forcer écrasement
python manage.py collectstatic --noinput --clear
```

### Gunicorn
```bash
# Lancer Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Avec workers multiples
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000

# Avec timeout
gunicorn config.wsgi:application \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120

# Avec logs
gunicorn config.wsgi:application \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Systemd Services
```bash
# Démarrer service
sudo systemctl start spas-gunicorn
sudo systemctl start spas-celery

# Arrêter service
sudo systemctl stop spas-gunicorn
sudo systemctl stop spas-celery

# Redémarrer service
sudo systemctl restart spas-gunicorn
sudo systemctl restart spas-celery

# Voir statut
sudo systemctl status spas-gunicorn
sudo systemctl status spas-celery

# Activer au démarrage
sudo systemctl enable spas-gunicorn
sudo systemctl enable spas-celery

# Voir logs
sudo journalctl -u spas-gunicorn -f
sudo journalctl -u spas-celery -f
```

## Dépannage

### Problèmes Courants
```bash
# Redis ne démarre pas
redis-cli ping
# Si erreur: vérifier que redis-server est lancé
redis-server

# PostgreSQL connexion refusée
sudo systemctl status postgresql
sudo systemctl start postgresql

# Migrations en conflit
python manage.py migrate --fake authentication 0001
python manage.py migrate

# Réinitialiser DB complètement (ATTENTION: perte de données!)
python manage.py flush
python manage.py migrate
python manage.py createsuperuser

# Token blacklist erreur
python manage.py migrate token_blacklist

# Permissions fichiers
sudo chown -R $USER:$USER .
chmod -R 755 .

# Vider cache Python
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Debug Mode
```bash
# Activer debug (développement seulement!)
# Dans .env:
DEBUG=True

# Avec Django shell
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)

# Avec Django extensions
pip install django-extensions
python manage.py shell_plus --print-sql
```

## Raccourcis Utiles

### Aliases (ajouter à .bashrc ou .zshrc)
```bash
# Django
alias pm='python manage.py'
alias pms='python manage.py runserver'
alias pmm='python manage.py migrate'
alias pmmm='python manage.py makemigrations'
alias pms='python manage.py shell'
alias pmt='python manage.py test'

# Celery
alias cel='celery -A config'
alias celw='celery -A config worker -l info'
alias celb='celery -A config beat -l info'

# Redis
alias rc='redis-cli'
alias rcp='redis-cli ping'

# Logs
alias logs='tail -f logs/spas.log'
```

### Git Workflow
```bash
# Créer branche feature
git checkout -b feature/auth-improvements

# Commit
git add .
git commit -m "feat: add advanced JWT authentication"

# Push
git push origin feature/auth-improvements

# Merge dans main
git checkout main
git merge feature/auth-improvements
git push origin main

# Tag version
git tag -a v1.0.0 -m "Version 1.0.0 - Advanced Authentication"
git push origin v1.0.0
```

## Documentation et Help

### Django Commands Help
```bash
# Liste toutes les commandes
python manage.py help

# Help pour commande spécifique
python manage.py help migrate
python manage.py help createsuperuser

# Version Django
python manage.py version
```

### URLs et Endpoints
```bash
# Lister toutes les URLs
python manage.py show_urls  # Nécessite django-extensions

# Sans extensions
python manage.py shell
>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> for pattern in resolver.url_patterns:
...     print(pattern)
```

### Documentation API
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema JSON: http://localhost:8000/api/schema/

## Variables d'Environnement Importantes

```bash
# Voir toutes les variables
printenv | grep -i spas

# Définir temporairement
export DEBUG=True
export SECRET_KEY=temporary-key

# Définir pour une commande
DEBUG=True python manage.py runserver
```

---

**Astuce**: Ajouter ces commandes fréquentes à un Makefile pour simplification:

```makefile
.PHONY: run migrate test shell

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	python manage.py test

shell:
	python manage.py shell

celery:
	celery -A config worker -l info
```

Utilisation: `make run`, `make migrate`, etc.
