# SPAS - Guide de Gestion de la Base de Données PostgreSQL

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Configuration](#configuration)
3. [Installation et Setup Initial](#installation-et-setup-initial)
4. [Gestion des Migrations](#gestion-des-migrations)
5. [Scripts Disponibles](#scripts-disponibles)
6. [Commandes Courantes](#commandes-courantes)
7. [Résolution de Problèmes](#résolution-de-problèmes)
8. [Optimisation des Performances](#optimisation-des-performances)
9. [Sauvegarde et Restauration](#sauvegarde-et-restauration)

---

## Vue d'ensemble

SPAS utilise **PostgreSQL** comme système de gestion de base de données. La configuration est optimisée pour les performances et la fiabilité avec :

- Connection pooling (CONN_MAX_AGE = 600 secondes)
- Health checks automatiques
- Timeout des requêtes (30 secondes)
- Transactions atomiques par défaut
- Extensions PostgreSQL (uuid-ossp, pg_trgm)

### Architecture de la Base de Données

```
SPAS Database
├── users          - Utilisateurs et authentification
├── programs       - Programmes académiques
├── sessions       - Sessions académiques
├── students       - Étudiants
├── grades         - Notes et évaluations
├── attendance     - Présences
├── predictions    - Prédictions ML
├── alerts         - Alertes système
└── ml             - Modèles et configurations ML
```

---

## Configuration

### Variables d'Environnement (.env)

```bash
# Database Configuration
DB_NAME=spas_db
DB_USER=spas_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Database Performance (Optional)
DB_CONN_MAX_AGE=600  # Connection pool timeout (seconds)

# PostgreSQL Superuser (for initial setup)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
```

### Configuration Django (config/settings.py)

La configuration PostgreSQL dans Django inclut :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='spas_db'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        },
        'ATOMIC_REQUESTS': True,
    }
}
```

**Optimisations incluses :**
- ✅ Connection pooling (CONN_MAX_AGE)
- ✅ Health checks automatiques
- ✅ Timeout de connexion (10s)
- ✅ Timeout de requête (30s)
- ✅ Transactions atomiques par requête

---

## Installation et Setup Initial

### 1. Installer PostgreSQL

#### Windows
```powershell
# Télécharger depuis https://www.postgresql.org/download/windows/
# OU via Chocolatey
choco install postgresql
```

#### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Démarrer PostgreSQL

#### Windows
```powershell
# Vérifier le service
sc query postgresql-x64-14

# Démarrer le service
net start postgresql-x64-14
```

#### Linux
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS
```bash
brew services start postgresql
```

### 3. Setup de la Base de Données

#### Option A : Script Python Automatique (Recommandé)

```bash
# Créer .env depuis .env.example
cp .env.example .env
# Éditer .env avec vos configurations

# Exécuter le script de setup
python scripts/setup_database.py
```

Ce script va :
- ✅ Créer l'utilisateur PostgreSQL
- ✅ Créer la base de données
- ✅ Accorder les permissions
- ✅ Installer les extensions PostgreSQL

#### Option B : Scripts Shell/Batch

**Linux/Mac :**
```bash
chmod +x scripts/init_db.sh
./scripts/init_db.sh
```

**Windows :**
```batch
scripts\init_db.bat
```

#### Option C : Manuel via psql

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer l'utilisateur
CREATE USER spas_user WITH PASSWORD 'your_password';

# Créer la base de données
CREATE DATABASE spas_db OWNER spas_user;

# Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE spas_db TO spas_user;

# Se connecter à la base de données
\c spas_db

# Installer les extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

# Accorder les privilèges sur le schéma
GRANT ALL ON SCHEMA public TO spas_user;

\q
```

---

## Gestion des Migrations

### Ordre de Dépendance des Apps

Les migrations doivent être créées dans cet ordre en raison des dépendances :

1. **users** - Modèle User (AUTH_USER_MODEL)
2. **programs** - Programmes et matières
3. **sessions** - Sessions académiques
4. **students** - Étudiants (dépend de programs, sessions)
5. **grades** - Notes (dépend de students, programs, sessions)
6. **attendance** - Présences (dépend de students, sessions)
7. **ml** - Modèles ML
8. **predictions** - Prédictions (dépend de students, ml)
9. **alerts** - Alertes (dépend de students)

### Workflow de Migration Complet

#### Script Automatisé (Recommandé)

**Linux/Mac :**
```bash
chmod +x scripts/migrate.sh
./scripts/migrate.sh
```

**Windows :**
```batch
scripts\migrate.bat
```

**Options :**
```bash
# Migration normale
./scripts/migrate.sh

# Migration "fraîche" (supprime les anciennes migrations)
./scripts/migrate.sh --fresh
```

#### Commandes Manuelles

```bash
# 1. Vérifier l'état actuel
python manage.py showmigrations

# 2. Créer les migrations pour chaque app dans l'ordre
python manage.py makemigrations users
python manage.py makemigrations programs
python manage.py makemigrations sessions
python manage.py makemigrations students
python manage.py makemigrations grades
python manage.py makemigrations attendance
python manage.py makemigrations ml
python manage.py makemigrations predictions
python manage.py makemigrations alerts

# 3. Créer les migrations restantes
python manage.py makemigrations

# 4. Vérifier les migrations à appliquer
python manage.py showmigrations

# 5. Appliquer les migrations
python manage.py migrate

# 6. Vérifier que tout est appliqué
python manage.py showmigrations
```

### Migrations de Données Initiales

Les migrations de données créent des enregistrements de référence :

```bash
# Créer les migrations de données initiales
python scripts/create_initial_data_migrations.py

# Appliquer les migrations de données
python manage.py migrate
```

**Données créées :**
- ✅ Groupes d'utilisateurs et permissions
- ✅ Types d'alertes de référence
- ✅ Configurations système

---

## Scripts Disponibles

### 1. `setup_database.py`
**Usage :** Setup initial de la base de données PostgreSQL
```bash
python scripts/setup_database.py
```

**Fonctions :**
- Créer utilisateur et base de données
- Accorder permissions
- Installer extensions PostgreSQL

### 2. `migrate.sh / migrate.bat`
**Usage :** Gestion complète des migrations
```bash
./scripts/migrate.sh [--fresh]
```

**Fonctions :**
- Créer migrations dans l'ordre de dépendance
- Appliquer migrations
- Vérifier conflits
- Créer tables de cache

### 3. `check_migrations.py`
**Usage :** Vérifier l'état des migrations
```bash
python scripts/check_migrations.py
```

**Fonctions :**
- Vérifier connexion base de données
- Lister migrations appliquées/non appliquées
- Détecter conflits
- Vérifier cohérence modèles/migrations

### 4. `reset_db.sh / reset_db.bat`
**Usage :** Réinitialiser la base de données (DÉVELOPPEMENT SEULEMENT)
```bash
./scripts/reset_db.sh
```

**⚠️ ATTENTION : Supprime toutes les données !**

### 5. `create_initial_data_migrations.py`
**Usage :** Créer migrations de données initiales
```bash
python scripts/create_initial_data_migrations.py
```

---

## Commandes Courantes

### Vérification et Diagnostic

```bash
# Vérifier l'état des migrations
python manage.py showmigrations

# Vérifier si des migrations sont nécessaires
python manage.py makemigrations --check --dry-run

# Voir le plan de migration
python manage.py migrate --plan

# Lister les migrations appliquées
python manage.py showmigrations --list

# Vérifier l'état complet
python scripts/check_migrations.py
```

### Création de Migrations

```bash
# Créer migrations pour toutes les apps
python manage.py makemigrations

# Créer migration pour une app spécifique
python manage.py makemigrations users

# Créer migration avec nom custom
python manage.py makemigrations --name add_user_phone_field users

# Créer migration vide (pour data migration)
python manage.py makemigrations --empty users
```

### Application de Migrations

```bash
# Appliquer toutes les migrations
python manage.py migrate

# Appliquer migrations pour une app
python manage.py migrate users

# Appliquer jusqu'à une migration spécifique
python manage.py migrate users 0003

# Simuler migration (dry-run)
python manage.py migrate --plan
```

### Rollback de Migrations

```bash
# Revenir à la migration précédente
python manage.py migrate users 0002

# Annuler toutes les migrations d'une app
python manage.py migrate users zero

# ⚠️ Utiliser avec précaution en production !
```

### Base de Données

```bash
# Accéder au shell PostgreSQL
python manage.py dbshell

# Créer un superuser
python manage.py createsuperuser

# Vider une table (garder structure)
python manage.py flush

# Charger des fixtures
python manage.py loaddata fixtures/initial_data.json

# Exporter des données en fixture
python manage.py dumpdata users --indent 2 > fixtures/users.json
```

---

## Résolution de Problèmes

### Problème : "relation does not exist"

**Cause :** Tables non créées ou migrations non appliquées

**Solution :**
```bash
python manage.py migrate
```

### Problème : "duplicate key value violates unique constraint"

**Cause :** Tentative d'insertion de données en double

**Solution :**
```bash
# Vérifier les données existantes
python manage.py dbshell
SELECT * FROM table_name WHERE unique_field = 'value';

# Nettoyer ou modifier les données
```

### Problème : "migration conflicts detected"

**Cause :** Plusieurs migrations avec le même numéro

**Solution :**
```bash
# Voir les conflits
python scripts/check_migrations.py

# Option 1: Fusionner les migrations
python manage.py makemigrations --merge

# Option 2: Supprimer et recréer
rm apps/appname/migrations/000X_*.py
python manage.py makemigrations appname
```

### Problème : "could not connect to server"

**Cause :** PostgreSQL n'est pas démarré

**Solution :**
```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### Problème : "password authentication failed"

**Cause :** Mauvais credentials dans .env

**Solution :**
```bash
# Vérifier .env
cat .env | grep DB_

# Réinitialiser le mot de passe PostgreSQL
psql -U postgres
ALTER USER spas_user WITH PASSWORD 'new_password';
\q

# Mettre à jour .env
```

### Problème : "custom user model not found"

**Cause :** Migrations users pas appliquées en premier

**Solution :**
```bash
# Appliquer migrations users d'abord
python manage.py migrate users
python manage.py migrate
```

---

## Optimisation des Performances

### 1. Connection Pooling

Déjà configuré dans `settings.py` :
```python
'CONN_MAX_AGE': 600  # Garde connexions ouvertes 10 minutes
'CONN_HEALTH_CHECKS': True
```

### 2. Index de Base de Données

Tous les modèles incluent des index optimisés :
```python
class Meta:
    indexes = [
        models.Index(fields=['field_name']),
        models.Index(fields=['field1', 'field2']),
    ]
```

### 3. Query Optimization

```python
# Utiliser select_related pour ForeignKey
students = Student.objects.select_related('program', 'session')

# Utiliser prefetch_related pour ManyToMany et reverse ForeignKey
students = Student.objects.prefetch_related('grades', 'attendance')

# Éviter N+1 queries
students = Student.objects.select_related('program').prefetch_related('grades')
```

### 4. Database Caching

```bash
# Créer table de cache
python manage.py createcachetable

# Dans settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'spas_cache_table',
    }
}
```

### 5. Analyse de Requêtes Lentes

```python
# settings.py - Activer logging SQL en développement
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

```bash
# PostgreSQL - Analyser une requête
psql -U spas_user -d spas_db
EXPLAIN ANALYZE SELECT * FROM students WHERE risk_level = 'high';
```

### 6. Vacuum et Maintenance

```sql
-- Dans psql
VACUUM ANALYZE;  -- Nettoyer et analyser
REINDEX DATABASE spas_db;  -- Reconstruire index
```

---

## Sauvegarde et Restauration

### Backup Complet

```bash
# Backup de la base de données
pg_dump -U spas_user -h localhost -d spas_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup avec compression
pg_dump -U spas_user -h localhost -d spas_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup format custom (recommandé)
pg_dump -U spas_user -h localhost -Fc -d spas_db > backup_$(date +%Y%m%d_%H%M%S).dump
```

### Restauration

```bash
# Depuis SQL
psql -U spas_user -h localhost -d spas_db < backup.sql

# Depuis SQL compressé
gunzip -c backup.sql.gz | psql -U spas_user -h localhost -d spas_db

# Depuis format custom
pg_restore -U spas_user -h localhost -d spas_db backup.dump

# Restauration avec drop/create
dropdb -U postgres spas_db
createdb -U postgres -O spas_user spas_db
psql -U spas_user -d spas_db < backup.sql
```

### Backup Automatique (Script)

Créer un script de backup automatique :

```bash
#!/bin/bash
# backup_spas.sh

BACKUP_DIR="/backups/spas"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="spas_backup_${DATE}.dump"

mkdir -p $BACKUP_DIR

pg_dump -U spas_user -h localhost -Fc -d spas_db > "${BACKUP_DIR}/${FILENAME}"

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "spas_backup_*.dump" -mtime +7 -delete

echo "Backup créé: ${FILENAME}"
```

Configuration cron (Linux) :
```bash
# Backup quotidien à 2h du matin
0 2 * * * /path/to/backup_spas.sh
```

---

## Environnements Multiples

### Développement
```bash
# .env.development
DB_NAME=spas_db_dev
DB_USER=spas_dev
DEBUG=True
```

### Testing
```bash
# .env.testing
DB_NAME=spas_db_test
DB_USER=spas_test
DEBUG=False
```

### Production
```bash
# .env.production
DB_NAME=spas_db_prod
DB_USER=spas_prod
DB_CONN_MAX_AGE=600
DEBUG=False
```

Utilisation :
```bash
# Spécifier environnement
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
```

---

## Checklist de Déploiement Production

- [ ] Variables d'environnement sécurisées (.env)
- [ ] Mot de passe DB fort et unique
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configuré
- [ ] Connection pooling activé (CONN_MAX_AGE)
- [ ] Backups automatiques configurés
- [ ] Monitoring PostgreSQL actif
- [ ] SSL/TLS pour connexions DB activé
- [ ] Firewall configuré (port 5432)
- [ ] pg_hba.conf sécurisé
- [ ] Logs PostgreSQL activés
- [ ] Vacuum automatique configuré

---

## Ressources Additionnelles

- [Django Database Documentation](https://docs.djangoproject.com/en/5.0/ref/databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Migrations Documentation](https://docs.djangoproject.com/en/5.0/topics/migrations/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

**Dernière mise à jour :** 2026-01-02
**Version :** 1.0.0
