# Quick Start - Installation Rapide du Système de Sécurité SPAS

## Installation en 10 Minutes

### Étape 1: Vérifier les fichiers (30 secondes)

```bash
# Vérifier que tous les fichiers sont présents
ls backend/apps/core/
# Devrait afficher: __init__.py, apps.py, admin.py, models.py, permissions.py, mixins.py, throttling.py, middleware.py, utils.py, README.md, INSTALLATION.md, tests/
```

### Étape 2: Modifier settings.py (5 minutes)

Ouvrir `backend/config/settings.py` et faire les modifications suivantes:

#### A. Ajouter 'apps.core' dans INSTALLED_APPS (ligne ~44)

```python
INSTALLED_APPS = [
    # ... apps Django existantes ...

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',

    # Local apps
    'apps.core',  # <-- AJOUTER CETTE LIGNE ICI
    'apps.authentication',
    'apps.users',
    'apps.students',
    # ... autres apps
]
```

#### B. Ajouter les middleware (ligne ~61)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # AJOUTER CES 3 LIGNES:
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.AuditMiddleware',
    'apps.core.middleware.PermissionDeniedLoggingMiddleware',
]
```

#### C. Mettre à jour REST_FRAMEWORK (ligne ~169)

Remplacer la section `DEFAULT_THROTTLE_CLASSES` et `DEFAULT_THROTTLE_RATES`:

```python
REST_FRAMEWORK = {
    # ... autres configurations ...

    'DEFAULT_THROTTLE_CLASSES': (
        'apps.core.throttling.BurstRateThrottle',
        'apps.core.throttling.SustainedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/min',
        'sustained': '1000/hour',
        'admin': '10000/hour',
        'ds': '5000/hour',
        'pedagogical': '3000/hour',
        'teacher': '2000/hour',
        'ml_prediction': '100/hour',
        'data_export': '50/hour',
        'anon_strict': '20/hour',
        'login': '5/minute',
        'register': '3/day',
        'password_reset': '3/hour',
        'email_verification': '3/hour',
        'token_refresh': '30/hour',
    },

    # ... autres configurations ...
}
```

#### D. Ajouter logger pour core (ligne ~320)

Dans la section `LOGGING`, ajouter:

```python
LOGGING = {
    # ... configuration existante ...
    'loggers': {
        # ... autres loggers ...
        'apps.core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Étape 3: Créer le répertoire logs (30 secondes)

```bash
# Sur Linux/Mac:
mkdir -p backend/logs

# Sur Windows PowerShell:
New-Item -ItemType Directory -Force -Path backend/logs
```

### Étape 4: Créer et appliquer les migrations (2 minutes)

```bash
cd backend

# Créer les migrations
python manage.py makemigrations core

# Appliquer les migrations
python manage.py migrate core
```

### Étape 5: Lancer les tests (1 minute)

```bash
# Tester que tout fonctionne
python manage.py test apps.core
```

Si tous les tests passent, l'installation est réussie !

### Étape 6: Vérifier dans le shell (1 minute)

```bash
python manage.py shell
```

```python
# Dans le shell Python
from apps.core.permissions import IsAdmin, CanManageStudents
from apps.core.models import AuditLog
from apps.core.mixins import RoleBasedPermissionMixin

# Tester la création d'un log
from apps.users.models import User
user = User.objects.first()

if user:
    log = AuditLog.log_action(
        user=user,
        action=AuditLog.Action.LOGIN,
        ip_address='127.0.0.1'
    )
    print(f"✓ Log créé: {log}")
    print(f"✓ Total logs: {AuditLog.objects.count()}")
else:
    print("Créez d'abord un utilisateur")

exit()
```

### Étape 7: Créer un superuser (optionnel)

```bash
python manage.py createsuperuser
# Email: admin@example.com
# Password: (votre mot de passe sécurisé)
```

### Étape 8: Lancer le serveur et tester

```bash
python manage.py runserver
```

Accéder à: http://localhost:8000/admin/core/auditlog/

## Commandes de Vérification

### Vérifier l'installation

```bash
# Vérifier les migrations
python manage.py showmigrations core

# Vérifier la configuration
python manage.py check

# Compter les logs d'audit
python manage.py shell -c "from apps.core.models import AuditLog; print(f'Logs: {AuditLog.objects.count()}')"

# Lancer tous les tests
python manage.py test apps.core --verbosity=2
```

## Utilisation Immédiate

### Appliquer à un ViewSet

Exemple minimal pour commencer:

```python
# Dans n'importe quel views.py
from apps.core.mixins import RoleBasedPermissionMixin, AuditLogMixin
from apps.core.permissions import IsTeacherOrAdmin, IsPedagogicalOrAbove
from rest_framework import viewsets

class MyViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    viewsets.ModelViewSet
):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer

    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'destroy': [IsAdmin],
    }

    audit_log_actions = ['create', 'update', 'destroy']
```

## Prochaines Étapes

1. **Lire la documentation**
   - SECURITY_SYSTEM_SUMMARY.md - Vue d'ensemble (10 min)
   - apps/core/README.md - Documentation complète (20 min)

2. **Voir l'exemple complet**
   - apps/students/views_with_permissions.py - Exemple détaillé

3. **Appliquer aux ViewSets**
   - Suivre SECURITY_IMPLEMENTATION_GUIDE.md

## Dépannage Rapide

### Problème: Module 'apps.core' not found

```bash
# Vérifier que 'apps.core' est dans INSTALLED_APPS
grep "apps.core" backend/config/settings.py

# Devrait afficher: 'apps.core',
```

### Problème: Migrations error

```bash
# Supprimer les migrations et recommencer
rm backend/apps/core/migrations/0001_initial.py
python manage.py makemigrations core
python manage.py migrate core
```

### Problème: Tests failed

```bash
# Lancer les tests avec plus de détails
python manage.py test apps.core --verbosity=2

# Vérifier les imports
python manage.py shell -c "from apps.core.permissions import IsAdmin; print('OK')"
```

### Problème: Cannot access /admin/

```bash
# Créer un superuser
python manage.py createsuperuser

# Vérifier que l'utilisateur est bien créé
python manage.py shell -c "from apps.users.models import User; print(User.objects.filter(is_superuser=True).count())"
```

## Checklist d'Installation

- [ ] Fichiers présents dans apps/core/
- [ ] settings.py modifié (INSTALLED_APPS)
- [ ] settings.py modifié (MIDDLEWARE)
- [ ] settings.py modifié (REST_FRAMEWORK)
- [ ] settings.py modifié (LOGGING)
- [ ] Répertoire logs créé
- [ ] Migrations créées
- [ ] Migrations appliquées
- [ ] Tests passent (tous verts)
- [ ] Shell Django fonctionne
- [ ] Admin accessible
- [ ] AuditLog visible dans l'admin

## Commandes Utiles

```bash
# Installation complète en une commande
cd backend && \
mkdir -p logs && \
python manage.py makemigrations core && \
python manage.py migrate core && \
python manage.py test apps.core

# Créer des utilisateurs de test
python manage.py shell << EOF
from apps.users.models import User

User.objects.create_user(
    email='admin@test.com',
    password='test123',
    first_name='Admin',
    last_name='Test',
    role=User.Role.ADMIN
)

User.objects.create_user(
    email='teacher@test.com',
    password='test123',
    first_name='Teacher',
    last_name='Test',
    role=User.Role.TEACHER
)

print("✓ Utilisateurs créés")
EOF

# Vérifier les logs
python manage.py shell -c "from apps.core.models import AuditLog; print(AuditLog.objects.all())"
```

## Test de Permissions via API

```bash
# 1. Obtenir un token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "test123"}'

# 2. Utiliser le token (remplacer YOUR_TOKEN)
curl -X GET http://localhost:8000/api/students/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Vérifier les logs d'audit
# Accéder à: http://localhost:8000/admin/core/auditlog/
```

## Résumé

**Installation complète:**
- Temps: ~10 minutes
- Étapes: 8
- Fichiers modifiés: 1 (settings.py)
- Commandes: 5-6

**Résultat:**
- Système de permissions opérationnel
- Audit logging actif
- Rate limiting configuré
- Middleware de sécurité activés
- Tests validés

## Support

Pour plus d'aide:
- Documentation: `backend/apps/core/README.md`
- Installation détaillée: `backend/apps/core/INSTALLATION.md`
- Guide complet: `backend/SECURITY_IMPLEMENTATION_GUIDE.md`
- Résumé: `SECURITY_SYSTEM_SUMMARY.md`
- Fichiers: `FILES_CREATED.md`

**Tout est prêt ! Le système de sécurité est maintenant opérationnel.**
