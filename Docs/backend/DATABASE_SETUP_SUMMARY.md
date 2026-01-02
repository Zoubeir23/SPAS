# Configuration PostgreSQL et Migrations - Résumé

## Ce qui a été configuré

### 1. Configuration PostgreSQL Optimisée (config/settings.py)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... credentials ...
        'CONN_MAX_AGE': 600,           # Connection pooling (10 min)
        'CONN_HEALTH_CHECKS': True,    # Health checks automatiques
        'OPTIONS': {
            'connect_timeout': 10,     # Timeout connexion
            'options': '-c statement_timeout=30000'  # Timeout requête (30s)
        },
        'ATOMIC_REQUESTS': True,       # Transactions atomiques
    }
}
```

**Optimisations incluses:**
- Connection pooling pour réduire la latence
- Health checks automatiques des connexions
- Timeouts configurés pour éviter les blocages
- Transactions atomiques par défaut
- psycopg2-binary configuré dans requirements.txt

### 2. Scripts de Setup et Migration

#### `C:\Users\Public\Libraries\one\SPAS\backend\scripts\setup_database.py`
Script Python pour setup automatique de PostgreSQL:
- Créer utilisateur et base de données
- Accorder permissions
- Installer extensions (uuid-ossp, pg_trgm)
- Messages colorés et gestion d'erreurs

**Usage:**
```bash
python scripts/setup_database.py
```

#### `C:\Users\Public\Libraries\one\SPAS\backend\scripts\migrate.sh` (Linux/Mac)
#### `C:\Users\Public\Libraries\one\SPAS\backend\scripts\migrate.bat` (Windows)
Scripts complets de migration:
- Créer migrations dans l'ordre de dépendance
- Vérifier conflits
- Appliquer migrations
- Support mode --fresh

**Usage:**
```bash
./scripts/migrate.sh [--fresh]
scripts\migrate.bat [--fresh]
```

#### `C:\Users\Public\Libraries\one\SPAS\backend\scripts\check_migrations.py`
Script de diagnostic complet:
- Vérifier connexion base de données
- Lister migrations appliquées/non appliquées
- Détecter conflits
- Vérifier cohérence modèles/migrations

**Usage:**
```bash
python scripts/check_migrations.py
```

#### `C:\Users\Public\Libraries\one\SPAS\backend\scripts\create_initial_data_migrations.py`
Créer migrations de données initiales:
- Groupes utilisateurs et permissions
- Types d'alertes de référence

**Usage:**
```bash
python scripts/create_initial_data_migrations.py
```

### 3. Documentation

#### `C:\Users\Public\Libraries\one\SPAS\backend\README_DATABASE.md`
Documentation complète (60+ sections) couvrant:
- Configuration PostgreSQL
- Installation et setup
- Gestion des migrations
- Scripts disponibles
- Commandes courantes
- Résolution de problèmes
- Optimisation des performances
- Sauvegarde et restauration
- Environnements multiples
- Checklist de production

#### `C:\Users\Public\Libraries\one\SPAS\backend\MIGRATION_GUIDE.md`
Guide de référence rapide:
- Commandes essentielles
- Workflow quotidien
- Ordre de dépendance des apps
- Problèmes courants et solutions
- Backup & restore

### 4. Variables d'Environnement

#### `C:\Users\Public\Libraries\one\SPAS\backend\.env.example`
Fichier .env mis à jour avec:
- Configuration PostgreSQL complète
- Variables de performance (DB_CONN_MAX_AGE)
- Credentials superuser pour setup
- Toutes les variables nécessaires

## Ordre de Dépendance des Apps

Les migrations doivent être créées dans cet ordre:

1. **users** - Modèle User personnalisé (AUTH_USER_MODEL)
2. **programs** - Programmes et matières
3. **sessions** - Sessions académiques
4. **students** - Étudiants (dépend de programs, sessions)
5. **grades** - Notes (dépend de students, programs, sessions)
6. **attendance** - Présences (dépend de students, sessions)
7. **ml** - Modèles ML
8. **predictions** - Prédictions (dépend de students, ml)
9. **alerts** - Alertes (dépend de students)

## Workflow de Setup Initial

### Étape 1: Configurer l'environnement
```bash
# Copier .env.example vers .env
cp .env.example .env

# Éditer .env avec vos credentials
# Changer DB_PASSWORD, POSTGRES_PASSWORD, SECRET_KEY
```

### Étape 2: Setup PostgreSQL
```bash
# Option A: Script Python automatique (Recommandé)
python scripts/setup_database.py

# Option B: Scripts Shell/Batch
./scripts/init_db.sh        # Linux/Mac
scripts\init_db.bat         # Windows
```

### Étape 3: Créer et appliquer migrations
```bash
# Option A: Script automatique (Recommandé)
./scripts/migrate.sh        # Linux/Mac
scripts\migrate.bat         # Windows

# Option B: Manuel
python manage.py makemigrations users
python manage.py makemigrations programs
python manage.py makemigrations sessions
python manage.py makemigrations students
python manage.py makemigrations grades
python manage.py makemigrations attendance
python manage.py makemigrations ml
python manage.py makemigrations predictions
python manage.py makemigrations alerts
python manage.py migrate
```

### Étape 4: Créer données initiales
```bash
# Créer migrations de données
python scripts/create_initial_data_migrations.py

# Appliquer migrations de données
python manage.py migrate

# Créer superuser
python manage.py createsuperuser --email admin@spas.local
```

### Étape 5: Vérifier
```bash
# Vérifier l'état complet
python scripts/check_migrations.py

# Voir les migrations appliquées
python manage.py showmigrations
```

## Commandes Courantes

### Vérification
```bash
# Vérifier l'état des migrations
python manage.py showmigrations

# Vérifier si des migrations sont nécessaires
python manage.py makemigrations --check

# Diagnostic complet
python scripts/check_migrations.py
```

### Création de migrations
```bash
# Créer migrations pour toutes les apps
python manage.py makemigrations

# Créer pour une app spécifique
python manage.py makemigrations users

# Migration vide (pour data migration)
python manage.py makemigrations --empty users
```

### Application de migrations
```bash
# Appliquer toutes
python manage.py migrate

# Appliquer pour une app
python manage.py migrate users

# Voir le plan
python manage.py migrate --plan
```

### Base de données
```bash
# Shell PostgreSQL
python manage.py dbshell

# Créer superuser
python manage.py createsuperuser

# Reset DB (DEV SEULEMENT!)
./scripts/reset_db.sh
```

## Résolution de Problèmes

### "could not connect to server"
```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### "password authentication failed"
Vérifier les credentials dans `.env`:
```bash
cat .env | grep DB_
```

### "relation does not exist"
Appliquer les migrations:
```bash
python manage.py migrate
```

### "migration conflicts detected"
Fusionner les migrations:
```bash
python manage.py makemigrations --merge
```

## Fichiers Créés/Modifiés

### Nouveaux fichiers:
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\setup_database.py`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\migrate.sh`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\migrate.bat`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\check_migrations.py`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\create_initial_data_migrations.py`
- `C:\Users\Public\Libraries\one\SPAS\backend\README_DATABASE.md`
- `C:\Users\Public\Libraries\one\SPAS\backend\MIGRATION_GUIDE.md`
- `C:\Users\Public\Libraries\one\SPAS\backend\DATABASE_SETUP_SUMMARY.md` (ce fichier)

### Fichiers modifiés:
- `C:\Users\Public\Libraries\one\SPAS\backend\config\settings.py` - Optimisations PostgreSQL
- `C:\Users\Public\Libraries\one\SPAS\backend\.env.example` - Variables DB ajoutées

### Fichiers existants (non modifiés):
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\init_db.sh`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\init_db.bat`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\reset_db.sh`
- `C:\Users\Public\Libraries\one\SPAS\backend\scripts\reset_db.bat`

## Prochaines Étapes

1. **Configuration initiale:**
   - Copier `.env.example` vers `.env`
   - Configurer les credentials PostgreSQL
   - Démarrer PostgreSQL

2. **Setup de la base de données:**
   ```bash
   python scripts/setup_database.py
   ```

3. **Migrations:**
   ```bash
   ./scripts/migrate.sh        # Linux/Mac
   scripts\migrate.bat         # Windows
   ```

4. **Données initiales:**
   ```bash
   python scripts/create_initial_data_migrations.py
   python manage.py migrate
   ```

5. **Superuser:**
   ```bash
   python manage.py createsuperuser --email admin@spas.local
   ```

6. **Vérification:**
   ```bash
   python scripts/check_migrations.py
   ```

7. **Démarrer le serveur:**
   ```bash
   python manage.py runserver
   ```

## Optimisations PostgreSQL Appliquées

1. **Connection Pooling (CONN_MAX_AGE = 600s)**
   - Réutilise les connexions pendant 10 minutes
   - Réduit la latence de connexion

2. **Health Checks (CONN_HEALTH_CHECKS = True)**
   - Vérifie automatiquement la santé des connexions
   - Évite les erreurs de connexion fermée

3. **Timeouts Configurés**
   - Connect timeout: 10 secondes
   - Statement timeout: 30 secondes
   - Évite les blocages indéfinis

4. **Transactions Atomiques (ATOMIC_REQUESTS = True)**
   - Chaque requête HTTP est enveloppée dans une transaction
   - Garantit la cohérence des données

5. **Extensions PostgreSQL**
   - uuid-ossp: Génération d'UUIDs
   - pg_trgm: Optimisation de recherche texte

## Support et Documentation

- **Documentation complète:** `README_DATABASE.md`
- **Guide rapide:** `MIGRATION_GUIDE.md`
- **Support:** Voir les sections de résolution de problèmes dans README_DATABASE.md

---

**Créé le:** 2026-01-02
**Version:** 1.0.0
**Statut:** Prêt pour utilisation
