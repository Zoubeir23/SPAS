# SPAS - Guide Rapide des Migrations

## Commandes Essentielles

### Setup Initial

```bash
# 1. Configurer PostgreSQL
python scripts/setup_database.py

# 2. Exécuter toutes les migrations
./scripts/migrate.sh        # Linux/Mac
scripts\migrate.bat         # Windows

# 3. Créer un superuser
python manage.py createsuperuser --email admin@spas.local
```

### Workflow Quotidien

```bash
# Créer des migrations après modification de modèles
python manage.py makemigrations

# Vérifier ce qui va être migré
python manage.py migrate --plan

# Appliquer les migrations
python manage.py migrate

# Vérifier l'état
python scripts/check_migrations.py
```

## Ordre de Dépendance des Apps

**IMPORTANT:** Créer les migrations dans cet ordre:

1. `users` - Modèle User personnalisé
2. `programs` - Programmes et matières
3. `sessions` - Sessions académiques
4. `students` - Étudiants
5. `grades` - Notes
6. `attendance` - Présences
7. `ml` - Modèles ML
8. `predictions` - Prédictions
9. `alerts` - Alertes

## Scripts Disponibles

| Script | Usage | Description |
|--------|-------|-------------|
| `setup_database.py` | `python scripts/setup_database.py` | Setup initial PostgreSQL |
| `migrate.sh/.bat` | `./scripts/migrate.sh` | Migration complète automatique |
| `check_migrations.py` | `python scripts/check_migrations.py` | Vérifier l'état des migrations |
| `reset_db.sh/.bat` | `./scripts/reset_db.sh` | Réinitialiser la DB (DEV only) |

## Problèmes Courants

### "No migrations to apply"
```bash
# Créer les migrations manquantes
python manage.py makemigrations
```

### "Migration conflicts detected"
```bash
# Fusionner les migrations en conflit
python manage.py makemigrations --merge
```

### "relation does not exist"
```bash
# Appliquer toutes les migrations
python manage.py migrate
```

### "authentication failed"
```bash
# Vérifier les credentials dans .env
cat .env | grep DB_
```

## Commandes Utiles

```bash
# Voir toutes les migrations
python manage.py showmigrations

# Voir le plan de migration
python manage.py migrate --plan

# Annuler la dernière migration (PRUDENCE!)
python manage.py migrate appname 0002

# Accéder au shell PostgreSQL
python manage.py dbshell

# Vérifier la connexion DB
python scripts/check_migrations.py
```

## Backup & Restore

```bash
# Backup
pg_dump -U spas_user -d spas_db > backup.sql

# Restore
psql -U spas_user -d spas_db < backup.sql
```

## Variables d'Environnement (.env)

```bash
DB_NAME=spas_db
DB_USER=spas_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=600  # Connection pooling
```

## Configuration PostgreSQL

La configuration dans `settings.py` inclut:
- Connection pooling (CONN_MAX_AGE = 600s)
- Health checks automatiques
- Timeout connexion (10s)
- Timeout requête (30s)
- Transactions atomiques

## Documentation Complète

Pour plus de détails, voir: `README_DATABASE.md`

---

**Dernière mise à jour:** 2026-01-02
