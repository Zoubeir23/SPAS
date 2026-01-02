# Système de Permissions et Sécurité SPAS - Résumé

## Vue d'ensemble

Un système complet de permissions, d'audit et de sécurité a été implémenté pour le projet Django SPAS. Ce système fournit un contrôle d'accès basé sur les rôles (RBAC), une journalisation d'audit complète, et des mécanismes de sécurité robustes.

## Fichiers Créés

### Structure de l'App Core

```
backend/apps/core/
├── __init__.py                    # Configuration de l'app
├── apps.py                        # Configuration Django app
├── admin.py                       # Interface admin pour AuditLog
├── models.py                      # AuditLog et SoftDeleteModel
├── permissions.py                 # 12 classes de permissions personnalisées
├── mixins.py                      # 5 mixins réutilisables pour ViewSets
├── throttling.py                  # 9 classes de rate limiting
├── middleware.py                  # 5 middleware de sécurité
├── utils.py                       # Fonctions utilitaires
├── README.md                      # Documentation complète
├── INSTALLATION.md                # Guide d'installation
└── tests/
    ├── __init__.py
    ├── test_permissions.py        # Tests pour les permissions
    └── test_models.py             # Tests pour les modèles
```

### Documentation

```
backend/
├── SECURITY_IMPLEMENTATION_GUIDE.md    # Guide d'implémentation détaillé
└── apps/
    └── students/
        └── views_with_permissions.py   # Exemple complet d'implémentation
```

## Composants Implémentés

### 1. Permissions Personnalisées (12 classes)

| Permission | Description | Rôles Autorisés |
|-----------|-------------|-----------------|
| `IsAdmin` | Administrateurs uniquement | ADMIN |
| `IsTeacherOrAdmin` | Enseignants et admins | TEACHER, ADMIN |
| `IsDSOrAdmin` | DS et admins | DS, ADMIN |
| `IsPedagogicalOrAbove` | Conseillers pédagogiques et supérieurs | PEDAGOGICAL, DS, ADMIN |
| `IsOwnerOrReadOnly` | Propriétaire en écriture, autres en lecture | Propriétaire + ADMIN |
| `IsStudentOwner` | Étudiant pour ses propres données | Étudiant propriétaire |
| `CanManageStudents` | Gestion des étudiants | TEACHER (leurs), DS, ADMIN |
| `CanViewPredictions` | Voir les prédictions ML | TEACHER (leurs), PEDAGOGICAL, DS, ADMIN |
| `CanManageAlerts` | Gérer les alertes | TEACHER, DS, ADMIN |
| `CanRunMLPredictions` | Lancer des prédictions ML | DS, ADMIN |
| `ReadOnlyPermission` | Lecture seule | Tous authentifiés |

**Fichier**: `backend/apps/core/permissions.py`

### 2. Mixins pour ViewSets (5 mixins)

| Mixin | Fonctionnalité |
|-------|---------------|
| `RoleBasedPermissionMixin` | Permissions différentes par action |
| `AuditLogMixin` | Journalisation automatique des actions |
| `SoftDeleteMixin` | Suppression logique avec restore |
| `QuerySetFilterMixin` | Filtrage automatique par rôle |
| `ValidationMixin` | Hooks de validation personnalisés |

**Fichier**: `backend/apps/core/mixins.py`

### 3. Rate Limiting (9 classes)

| Throttle | Limite | Usage |
|----------|--------|-------|
| `AdminRateThrottle` | 10,000/heure | Admins |
| `DSRateThrottle` | 5,000/heure | DS |
| `PedagogicalRateThrottle` | 3,000/heure | Conseillers pédagogiques |
| `TeacherRateThrottle` | 2,000/heure | Enseignants |
| `BurstRateThrottle` | 60/minute | Prévention rafales |
| `SustainedRateThrottle` | 1,000/heure | Limite globale |
| `MLPredictionThrottle` | 100/heure (admin/ds) | Prédictions ML |
| `DataExportThrottle` | 50/heure (admin/ds) | Exports de données |
| `StrictAnonRateThrottle` | 20/heure | Utilisateurs anonymes |

**Fichier**: `backend/apps/core/throttling.py`

### 4. Modèles

#### AuditLog
Journalise toutes les actions importantes:
- Utilisateur
- Action (CREATE, UPDATE, DELETE, etc.)
- Objet affecté
- Changements (JSON)
- IP, User Agent, Endpoint
- Timestamp
- Données supplémentaires

#### SoftDeleteModel
Modèle abstrait pour suppression logique:
- `is_deleted` flag
- `deleted_at` timestamp
- `deleted_by` utilisateur
- Méthodes: `delete()`, `hard_delete()`, `restore()`
- Managers: `objects`, `all_with_deleted()`, `deleted_only()`

**Fichier**: `backend/apps/core/models.py`

### 5. Middleware (5 middleware)

| Middleware | Fonction |
|-----------|----------|
| `SecurityHeadersMiddleware` | Ajoute en-têtes de sécurité (CSP, XSS, etc.) |
| `AuditMiddleware` | Journalise les requêtes non-GET |
| `PermissionDeniedLoggingMiddleware` | Log les accès refusés (401/403) |
| `RateLimitMiddleware` | Rate limiting de fallback par IP |
| `RequestLoggingMiddleware` | Log toutes les requêtes (DEBUG) |

**Fichier**: `backend/apps/core/middleware.py`

### 6. Utilitaires

- `get_client_ip()`: Obtenir l'IP réelle du client
- `get_changes_dict()`: Créer un dict des changements
- `sanitize_sensitive_data()`: Masquer données sensibles

**Fichier**: `backend/apps/core/utils.py`

## Rôles Utilisateur

### ADMIN (Administrateur)
- **Accès**: Complet sur toutes les ressources
- **Permissions**: Toutes les opérations CRUD
- **Rate Limit**: 10,000 req/heure
- **Filtrage**: Voit tout

### DS (Directeur des Études)
- **Accès**: Supervision complète des opérations académiques
- **Permissions**: CRUD sur étudiants, prédictions ML, alertes
- **Rate Limit**: 5,000 req/heure
- **Filtrage**: Voit tout

### PEDAGOGICAL (Conseiller Pédagogique)
- **Accès**: Consultation et analyse
- **Permissions**: Lecture sur tout, pas de création/modification
- **Rate Limit**: 3,000 req/heure
- **Filtrage**: Voit tout (lecture seule)

### TEACHER (Enseignant)
- **Accès**: Gestion de ses étudiants et classes
- **Permissions**: CRUD sur ses étudiants, notes, assiduité
- **Rate Limit**: 2,000 req/heure
- **Filtrage**: Voit seulement ses étudiants

## Matrice des Permissions par Resource

| Resource | List | Retrieve | Create | Update | Delete |
|----------|------|----------|--------|--------|--------|
| **Students** | PEDAGOGICAL+ | PEDAGOGICAL+ | TEACHER+ | TEACHER+ | ADMIN |
| **Grades** | PEDAGOGICAL+ | PEDAGOGICAL+ | TEACHER+ | TEACHER+ | ADMIN |
| **Attendance** | PEDAGOGICAL+ | PEDAGOGICAL+ | TEACHER+ | TEACHER+ | ADMIN |
| **Predictions** | PEDAGOGICAL+ | PEDAGOGICAL+ | DS+ | DS+ | ADMIN |
| **Alerts** | PEDAGOGICAL+ | PEDAGOGICAL+ | TEACHER+ | TEACHER+ | ADMIN |
| **Programs** | ALL | ALL | DS+ | DS+ | DS+ |
| **Sessions** | ALL | ALL | DS+ | DS+ | DS+ |
| **ML Models** | PEDAGOGICAL+ | PEDAGOGICAL+ | DS+ | DS+ | ADMIN |

*Légende*: PEDAGOGICAL+ = PEDAGOGICAL, DS, ADMIN

## Fonctionnalités de Sécurité

### 1. Authentification et Autorisation
- JWT tokens avec rotation
- Email-based authentication
- Role-based access control (RBAC)
- Object-level permissions

### 2. Audit et Logging
- Audit complet de toutes les actions importantes
- Logs stockés en base de données
- Traçabilité complète (qui, quoi, quand, où)
- Interface admin pour consulter les logs

### 3. Rate Limiting
- Limites par rôle utilisateur
- Protection contre les abus
- Limites spéciales pour ML et exports
- Cache Redis pour performance

### 4. Protection des Données
- Soft deletion pour intégrité référentielle
- Validation des données sensibles
- Sanitisation des logs
- En-têtes de sécurité (CSP, HSTS, etc.)

### 5. Monitoring
- Logging des accès refusés
- Tracking des rate limit violations
- Logs structurés avec niveaux
- Logs séparés par app

## Exemple d'Utilisation

### ViewSet Complet avec Sécurité

```python
from apps.core.mixins import (
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    SoftDeleteMixin
)
from apps.core.permissions import (
    IsAdmin,
    IsTeacherOrAdmin,
    IsPedagogicalOrAbove,
    CanManageStudents
)

class StudentViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    SoftDeleteMixin,
    viewsets.ModelViewSet
):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    # Permissions par action
    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [CanManageStudents],
        'destroy': [IsAdmin],
    }

    # Audit automatique
    audit_log_actions = ['create', 'update', 'destroy']
    audit_log_changes = True

    # Filtrage par rôle
    filter_field = 'teacher'

    def get_queryset_for_teacher(self, queryset):
        return queryset.filter(teacher=self.request.user)
```

## Installation

### Étapes Rapides

```bash
# 1. L'app core est déjà créée dans apps/core/

# 2. Ajouter à settings.py (voir INSTALLATION.md)

# 3. Créer les migrations
python manage.py makemigrations core

# 4. Appliquer les migrations
python manage.py migrate core

# 5. Créer le répertoire logs
mkdir -p backend/logs

# 6. Lancer les tests
python manage.py test apps.core

# 7. Vérifier l'installation
python manage.py check
```

## Tests

### Couverture des Tests

- **test_permissions.py**: Tests pour toutes les classes de permissions
  - Tests par rôle
  - Tests des permissions au niveau objet
  - Tests des restrictions d'accès

- **test_models.py**: Tests pour les modèles
  - Tests de création d'audit logs
  - Tests de soft deletion
  - Tests de restoration

### Lancer les Tests

```bash
# Tous les tests core
python manage.py test apps.core

# Tests de permissions uniquement
python manage.py test apps.core.tests.test_permissions

# Tests avec verbose
python manage.py test apps.core --verbosity=2
```

## Documentation

### Fichiers de Documentation

1. **README.md** (`apps/core/README.md`)
   - Documentation complète de l'app core
   - Guide d'utilisation de chaque permission
   - Exemples d'utilisation des mixins

2. **INSTALLATION.md** (`apps/core/INSTALLATION.md`)
   - Guide d'installation étape par étape
   - Vérifications post-installation
   - Dépannage

3. **SECURITY_IMPLEMENTATION_GUIDE.md** (`backend/`)
   - Guide pour appliquer les permissions aux ViewSets
   - Exemples par app
   - Bonnes pratiques

4. **views_with_permissions.py** (`apps/students/`)
   - Exemple complet d'implémentation
   - Commentaires détaillés
   - Toutes les fonctionnalités démontrées

## Performance

### Optimisations

- **Cache Redis**: Rate limiting et tokens
- **Connection Pooling**: PostgreSQL
- **Query Optimization**: select_related, prefetch_related
- **Indexed Fields**: Tous les champs fréquemment filtrés
- **Lazy Loading**: Imports dans les méthodes

### Scalabilité

- **Horizontal Scaling**: Compatible avec load balancers
- **Async Ready**: Compatible avec Celery
- **Stateless**: JWT tokens (pas de session serveur)
- **Cache**: Tous les rate limits en cache

## Sécurité Production

### Checklist Production

- [ ] SECRET_KEY changé et sécurisé
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configuré
- [ ] HTTPS activé (SECURE_SSL_REDIRECT)
- [ ] Rate limiting activé
- [ ] Logs configurés avec rotation
- [ ] Redis sécurisé (password)
- [ ] PostgreSQL sécurisé
- [ ] Backup des AuditLogs
- [ ] Monitoring activé

### En-têtes de Sécurité Activés

- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy
- HSTS (Production)

## Maintenance

### Logs d'Audit

Les logs sont stockés indéfiniment par défaut. Pour nettoyer:

```python
# Dans le shell Django
from apps.core.models import AuditLog
from datetime import timedelta
from django.utils import timezone

# Supprimer les logs de plus de 1 an
cutoff = timezone.now() - timedelta(days=365)
AuditLog.objects.filter(timestamp__lt=cutoff).delete()
```

### Monitoring

Endpoints à monitorer:
- Taux d'accès refusés (401/403)
- Dépassements de rate limits (429)
- Erreurs serveur (500)
- Temps de réponse API

## Support et Ressources

### Documentation
- `backend/apps/core/README.md` - Guide complet
- `backend/apps/core/INSTALLATION.md` - Installation
- `backend/SECURITY_IMPLEMENTATION_GUIDE.md` - Implémentation

### Exemples
- `backend/apps/students/views_with_permissions.py` - ViewSet complet
- `backend/apps/core/tests/` - Tests unitaires

### Code
- `backend/apps/core/permissions.py` - 12 classes de permissions
- `backend/apps/core/mixins.py` - 5 mixins réutilisables
- `backend/apps/core/middleware.py` - 5 middleware de sécurité

## Conclusion

Le système de permissions et de sécurité SPAS fournit:

1. **Contrôle d'accès robuste** avec 12 classes de permissions
2. **Audit complet** avec journalisation automatique
3. **Protection contre les abus** avec rate limiting par rôle
4. **Intégrité des données** avec soft deletion
5. **Sécurité multi-couches** avec middleware spécialisés
6. **Facilité d'utilisation** avec mixins réutilisables
7. **Tests complets** pour garantir la fiabilité
8. **Documentation détaillée** pour faciliter l'adoption

Le système est prêt à être utilisé et peut être facilement étendu selon les besoins du projet.
