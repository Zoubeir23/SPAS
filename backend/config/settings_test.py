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

# Désactiver le throttling en test : le cache de throttle (LocMemCache) n'est
# pas réinitialisé entre les méthodes de test comme la base de données l'est,
# donc plusieurs TestCase appelant /login/ ou /register/ dans leur setUp()
# finissent par se faire mutuellement throttle. Aucun test ne vérifie le
# comportement de throttling lui-même.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
}
