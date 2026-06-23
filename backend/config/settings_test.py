"""
Settings de test — utilise SQLite en mémoire pour éviter PostgreSQL.
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Désactiver le cache Redis pour les tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Désactiver Celery pour les tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email en mode console
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Simplifier les logs en test
LOGGING = {}

# Désactiver la vérification CSRF
MIDDLEWARE = [m for m in MIDDLEWARE if 'csrf' not in m.lower()]  # noqa: F405

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Désactiver les redirections HTTPS en test
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
