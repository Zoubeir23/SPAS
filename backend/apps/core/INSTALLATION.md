# Installation du Système de Permissions et Sécurité SPAS

## Étapes d'Installation

### 1. Vérifier que tous les fichiers sont en place

Les fichiers suivants doivent exister dans `backend/apps/core/`:

```
apps/core/
├── __init__.py
├── admin.py
├── apps.py
├── middleware.py
├── mixins.py
├── models.py
├── permissions.py
├── throttling.py
├── utils.py
├── README.md
├── INSTALLATION.md
└── tests/
    ├── __init__.py
    ├── test_permissions.py
    └── test_models.py
```

### 2. Mettre à jour settings.py

Éditer `backend/config/settings.py`:

#### A. Ajouter 'apps.core' dans INSTALLED_APPS

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',

    # Local apps - AJOUTER 'apps.core' ICI
    'apps.core',  # <- AJOUTER CETTE LIGNE
    'apps.authentication',
    'apps.users',
    'apps.students',
    'apps.programs',
    'apps.sessions',
    'apps.grades',
    'apps.attendance',
    'apps.ml',
    'apps.predictions',
    'apps.alerts',
]
```

#### B. Ajouter les middleware de sécurité

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
    # AJOUTER CES LIGNES
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.AuditMiddleware',
    'apps.core.middleware.PermissionDeniedLoggingMiddleware',
]

# AJOUTER CECI
if DEBUG:
    MIDDLEWARE.append('apps.core.middleware.RequestLoggingMiddleware')
```

#### C. Mettre à jour REST_FRAMEWORK

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # MODIFIER CES LIGNES
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
    # ... autres configurations
}
```

#### D. Ajouter un logger pour core

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'spas.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.authentication': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        # AJOUTER CETTE SECTION
        'apps.core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 3. Créer et appliquer les migrations

```bash
cd backend

# Créer les migrations
python manage.py makemigrations core

# Vérifier les migrations
python manage.py showmigrations core

# Appliquer les migrations
python manage.py migrate core
```

### 4. Créer le répertoire logs

```bash
# Créer le répertoire logs s'il n'existe pas
mkdir -p backend/logs

# Sur Windows (PowerShell):
# New-Item -ItemType Directory -Force -Path backend\logs
```

### 5. Vérifier l'installation

```bash
# Lancer le shell Django
python manage.py shell
```

```python
# Tester les imports
from apps.core.permissions import IsAdmin, CanManageStudents
from apps.core.models import AuditLog
from apps.core.mixins import RoleBasedPermissionMixin

# Tester la création d'un log d'audit
from apps.users.models import User
user = User.objects.first()

log = AuditLog.log_action(
    user=user,
    action=AuditLog.Action.LOGIN,
    ip_address='127.0.0.1'
)

print(f"Log créé: {log}")
print(f"Total logs: {AuditLog.objects.count()}")
```

### 6. Lancer les tests

```bash
# Tester les permissions
python manage.py test apps.core.tests.test_permissions

# Tester les modèles
python manage.py test apps.core.tests.test_models

# Tester toute l'app core
python manage.py test apps.core
```

### 7. Créer un superuser pour accéder à l'admin

```bash
python manage.py createsuperuser
# Email: admin@example.com
# Password: (votre mot de passe)
```

### 8. Accéder à l'admin et vérifier les logs

```bash
# Lancer le serveur
python manage.py runserver

# Accéder à:
# http://localhost:8000/admin/core/auditlog/
```

### 9. Tester les permissions via l'API

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'

# Utiliser le token pour tester les endpoints
curl -X GET http://localhost:8000/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Vérification Post-Installation

### Checklist

- [ ] App core installée dans INSTALLED_APPS
- [ ] Middleware de sécurité ajoutés
- [ ] Throttling configuré
- [ ] Logger configuré pour apps.core
- [ ] Migrations créées et appliquées
- [ ] Répertoire logs créé
- [ ] Tests passent avec succès
- [ ] Admin accessible et logs d'audit visibles
- [ ] Imports fonctionnent dans le shell

### Commandes de vérification

```bash
# Vérifier les migrations
python manage.py showmigrations core

# Vérifier les modèles
python manage.py shell -c "from apps.core.models import AuditLog; print(AuditLog.objects.count())"

# Vérifier les tests
python manage.py test apps.core --verbosity=2

# Vérifier la configuration
python manage.py check
```

## Prochaines Étapes

1. **Appliquer les permissions aux ViewSets existants**
   - Voir `SECURITY_IMPLEMENTATION_GUIDE.md`
   - Utiliser l'exemple dans `apps/students/views_with_permissions.py`

2. **Créer des utilisateurs de test**
   ```python
   python manage.py shell
   from apps.users.models import User

   # Créer un enseignant
   teacher = User.objects.create_user(
       email='teacher@test.com',
       password='test123',
       first_name='Jean',
       last_name='Dupont',
       role=User.Role.TEACHER
   )

   # Créer un DS
   ds = User.objects.create_user(
       email='ds@test.com',
       password='test123',
       first_name='Marie',
       last_name='Martin',
       role=User.Role.DS
   )
   ```

3. **Tester les différents scénarios**
   - Connexion avec différents rôles
   - Accès aux différents endpoints
   - Vérifier les logs d'audit
   - Tester les rate limits

## Dépannage

### Problème: ModuleNotFoundError: No module named 'apps.core'

**Solution**: Vérifier que 'apps.core' est bien dans INSTALLED_APPS et que le répertoire existe.

### Problème: Migration error

**Solution**:
```bash
python manage.py makemigrations --empty core
# Puis relancer makemigrations
python manage.py makemigrations core
```

### Problème: Import error dans les middleware

**Solution**: S'assurer que tous les fichiers de l'app core sont créés (permissions.py, utils.py, models.py).

### Problème: Redis connection error

**Solution**: Si Redis n'est pas installé, modifier le cache backend dans settings.py:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Problème: Logs directory not found

**Solution**:
```bash
mkdir -p backend/logs
chmod 755 backend/logs  # Sur Linux/Mac
```

## Support

Pour plus d'informations:
- README: `backend/apps/core/README.md`
- Guide d'implémentation: `backend/SECURITY_IMPLEMENTATION_GUIDE.md`
- Exemple: `backend/apps/students/views_with_permissions.py`
- Tests: `backend/apps/core/tests/`
