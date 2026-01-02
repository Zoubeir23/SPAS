# Configuration PostgreSQL et Migrations - COMPLET

## Statut: CONFIGURATION TERMINEE

Tous les fichiers et scripts nécessaires pour gérer PostgreSQL et les migrations Django ont été créés.

## Fichiers Créés

### Scripts de Setup et Migration

1. **`scripts/setup_database.py`**
   - Setup automatique PostgreSQL
   - Création utilisateur et base de données
   - Installation extensions (uuid-ossp, pg_trgm)
   - Gestion d'erreurs complète

   ```bash
   python scripts/setup_database.py
   ```

2. **`scripts/migrate.sh` / `scripts/migrate.bat`**
   - Migration complète automatique
   - Ordre de dépendance respecté
   - Support mode --fresh
   - Vérification de conflits

   ```bash
   ./scripts/migrate.sh [--fresh]      # Linux/Mac
   scripts\migrate.bat [--fresh]       # Windows
   ```

3. **`scripts/check_migrations.py`**
   - Diagnostic complet des migrations
   - Vérification connexion DB
   - Détection de conflits
   - Rapport détaillé

   ```bash
   python scripts/check_migrations.py
   ```

4. **`scripts/create_initial_data_migrations.py`**
   - Migrations de données initiales
   - Groupes et permissions utilisateurs
   - Types d'alertes

   ```bash
   python scripts/create_initial_data_migrations.py
   ```

### Documentation

5. **`README_DATABASE.md`**
   - Documentation complète (60+ sections)
   - Guide d'installation
   - Gestion des migrations
   - Résolution de problèmes
   - Optimisation performances
   - Sauvegarde/restauration
   - Checklist production

6. **`MIGRATION_GUIDE.md`**
   - Guide de référence rapide
   - Commandes essentielles
   - Workflow quotidien
   - Problèmes courants

7. **`DATABASE_SETUP_SUMMARY.md`**
   - Résumé complet de la configuration
   - Workflow de setup initial
   - Ordre de dépendance des apps
   - Prochaines étapes

### Configuration

8. **`config/settings.py`** (MODIFIE)
   - Configuration PostgreSQL optimisée
   - Connection pooling (CONN_MAX_AGE = 600s)
   - Health checks automatiques
   - Timeouts configurés
   - Transactions atomiques

9. **`.env.example`** (MODIFIE)
   - Variables PostgreSQL ajoutées
   - DB_CONN_MAX_AGE
   - POSTGRES_USER/PASSWORD pour setup
   - Documentation des variables

## Configuration PostgreSQL dans settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='spas_db'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        # Optimisations
        'CONN_MAX_AGE': env.int('DB_CONN_MAX_AGE', default=600),
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        },
        'ATOMIC_REQUESTS': True,
        'AUTOCOMMIT': True,
    }
}
```

## Ordre de Dépendance des Apps (IMPORTANT!)

Les migrations DOIVENT être créées dans cet ordre:

1. `users` - Custom User Model (AUTH_USER_MODEL)
2. `programs` - Programmes et matières
3. `sessions` - Sessions académiques
4. `students` - Étudiants (FK vers programs, sessions)
5. `grades` - Notes (FK vers students, programs, sessions)
6. `attendance` - Présences (FK vers students, sessions)
7. `ml` - Modèles ML
8. `predictions` - Prédictions (FK vers students, ml)
9. `alerts` - Alertes (FK vers students)

## Workflow de Setup Initial (Étape par Étape)

### 1. Configuration Environnement

```bash
# Copier et éditer .env
cp .env.example .env
nano .env  # ou votre éditeur

# Variables importantes à changer:
# - DB_PASSWORD=votre_mot_de_passe_securise
# - POSTGRES_PASSWORD=mot_de_passe_postgres
# - SECRET_KEY=votre_secret_key_unique
```

### 2. Installation PostgreSQL

**Si pas déjà installé:**

```bash
# Windows
# Télécharger: https://www.postgresql.org/download/windows/

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 3. Démarrer PostgreSQL

```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

### 4. Setup Base de Données

```bash
# Option A: Script automatique (RECOMMANDE)
python scripts/setup_database.py

# Option B: Script shell/batch
./scripts/init_db.sh        # Linux/Mac
scripts\init_db.bat         # Windows
```

### 5. Créer et Appliquer Migrations

```bash
# Option A: Script automatique (RECOMMANDE)
./scripts/migrate.sh        # Linux/Mac
scripts\migrate.bat         # Windows

# Option B: Manuel (respecter l'ordre!)
python manage.py makemigrations users
python manage.py makemigrations programs
python manage.py makemigrations sessions
python manage.py makemigrations students
python manage.py makemigrations grades
python manage.py makemigrations attendance
python manage.py makemigrations ml
python manage.py makemigrations predictions
python manage.py makemigrations alerts
python manage.py makemigrations  # Remaining
python manage.py migrate
```

### 6. Données Initiales

```bash
# Créer migrations de données
python scripts/create_initial_data_migrations.py

# Appliquer
python manage.py migrate
```

### 7. Créer Superuser

```bash
python manage.py createsuperuser --email admin@spas.local
# Suivre les prompts pour définir mot de passe
```

### 8. Vérification Finale

```bash
# Diagnostic complet
python scripts/check_migrations.py

# Voir migrations appliquées
python manage.py showmigrations

# Test connexion DB
python manage.py dbshell
\dt  # Liste tables
\q   # Quitter
```

### 9. Démarrer Serveur

```bash
python manage.py runserver
# Accéder: http://localhost:8000/admin
```

## Commandes de Maintenance Courantes

### Quotidien (Développement)

```bash
# Après modification de modèles
python manage.py makemigrations

# Vérifier ce qui va être migré
python manage.py migrate --plan

# Appliquer migrations
python manage.py migrate

# Vérifier état
python scripts/check_migrations.py
```

### Diagnostic

```bash
# État complet
python scripts/check_migrations.py

# Liste migrations
python manage.py showmigrations

# Vérifier si migrations nécessaires
python manage.py makemigrations --check

# Shell DB
python manage.py dbshell
```

### Reset (DEVELOPPEMENT SEULEMENT!)

```bash
# Reset complet DB
./scripts/reset_db.sh       # Linux/Mac
scripts\reset_db.bat        # Windows

# Migration fraîche
./scripts/migrate.sh --fresh
```

## Résolution Rapide de Problèmes

### PostgreSQL ne démarre pas
```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### Erreur d'authentification
```bash
# Vérifier .env
cat .env | grep DB_

# Réinitialiser mot de passe
psql -U postgres
ALTER USER spas_user WITH PASSWORD 'nouveau_mot_de_passe';
\q
```

### "relation does not exist"
```bash
python manage.py migrate
```

### Conflits de migration
```bash
python manage.py makemigrations --merge
```

### Vérifier connexion
```bash
python scripts/check_migrations.py
```

## Optimisations Appliquées

1. **Connection Pooling** - Connexions réutilisées pendant 10 min
2. **Health Checks** - Vérification automatique des connexions
3. **Timeouts** - Connexion (10s) et requête (30s)
4. **Transactions Atomiques** - Garantie de cohérence
5. **Extensions PostgreSQL** - uuid-ossp, pg_trgm

## Tests de Validation

Après le setup, tester:

```bash
# 1. Connexion DB
python scripts/check_migrations.py

# 2. Migrations appliquées
python manage.py showmigrations

# 3. Shell DB
python manage.py dbshell
SELECT COUNT(*) FROM users;
\q

# 4. Admin
python manage.py runserver
# Ouvrir: http://localhost:8000/admin
# Login avec superuser créé
```

## Backup Recommandé

Avant modifications importantes:

```bash
# Backup
pg_dump -U spas_user -d spas_db > backup_$(date +%Y%m%d).sql

# Restore (si nécessaire)
psql -U spas_user -d spas_db < backup_YYYYMMDD.sql
```

## Structure des Fichiers

```
backend/
├── config/
│   └── settings.py                    # MODIFIE - Config PostgreSQL optimisée
├── scripts/
│   ├── setup_database.py              # NOUVEAU - Setup auto PostgreSQL
│   ├── migrate.sh                     # NOUVEAU - Migration auto (Linux/Mac)
│   ├── migrate.bat                    # NOUVEAU - Migration auto (Windows)
│   ├── check_migrations.py            # NOUVEAU - Diagnostic migrations
│   ├── create_initial_data_migrations.py  # NOUVEAU - Data migrations
│   ├── init_db.sh                     # EXISTANT
│   ├── init_db.bat                    # EXISTANT
│   ├── reset_db.sh                    # EXISTANT
│   └── reset_db.bat                   # EXISTANT
├── .env.example                       # MODIFIE - Variables DB ajoutées
├── README_DATABASE.md                 # NOUVEAU - Doc complète
├── MIGRATION_GUIDE.md                 # NOUVEAU - Guide rapide
├── DATABASE_SETUP_SUMMARY.md          # NOUVEAU - Résumé config
└── POSTGRESQL_CONFIGURATION_COMPLETE.md  # NOUVEAU - Ce fichier
```

## Support et Documentation

- **Documentation complète:** `README_DATABASE.md` (60+ sections)
- **Guide rapide:** `MIGRATION_GUIDE.md`
- **Résumé setup:** `DATABASE_SETUP_SUMMARY.md`
- **Ce fichier:** Vue d'ensemble complète

## Prêt à Utiliser?

Suivez simplement le **Workflow de Setup Initial** ci-dessus, section par section.

En cas de problème, consultez:
1. Section "Résolution Rapide de Problèmes" ci-dessus
2. `README_DATABASE.md` - Section "Résolution de Problèmes"
3. `MIGRATION_GUIDE.md` - Section "Problèmes Courants"

---

**Configuration créée le:** 2026-01-02
**Status:** COMPLETE ET PRET POUR UTILISATION
**Version:** 1.0.0

**Note:** Ne PAS exécuter les migrations maintenant - juste préparer les scripts comme demandé.
