# Guide d'Implémentation de la Sécurité et des Permissions SPAS

## Introduction

Ce guide explique comment appliquer le système de permissions et de sécurité aux ViewSets existants du projet SPAS.

## Étape 1: Mettre à jour settings.py

Le fichier `config/settings.py` doit être mis à jour pour inclure l'app core et les middleware de sécurité.

### Modifications nécessaires:

```python
# Dans INSTALLED_APPS, ajouter 'apps.core' AVANT les autres apps locales
INSTALLED_APPS = [
    # ...
    'apps.core',  # Ajouter ici
    'apps.authentication',
    'apps.users',
    # ... autres apps
]

# Dans MIDDLEWARE, ajouter les middleware de sécurité
MIDDLEWARE = [
    # ... middleware Django existants
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.AuditMiddleware',
    'apps.core.middleware.PermissionDeniedLoggingMiddleware',
]

# En mode DEBUG, ajouter aussi:
if DEBUG:
    MIDDLEWARE.append('apps.core.middleware.RequestLoggingMiddleware')

# Dans REST_FRAMEWORK, mettre à jour les throttle classes
REST_FRAMEWORK = {
    # ... autres configurations
    'DEFAULT_THROTTLE_CLASSES': (
        'apps.core.throttling.BurstRateThrottle',
        'apps.core.throttling.SustainedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'burst': '60/min',
        'sustained': '1000/hour',
        'admin': '10000/hour',
        'ds': '5000/hour',
        'pedagogical': '3000/hour',
        'teacher': '2000/hour',
        'ml_prediction': '100/hour',
        'data_export': '50/hour',
        # ... autres rates
    },
}

# Ajouter un logger pour core
LOGGING = {
    # ...
    'loggers': {
        # ... autres loggers
        'apps.core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Étape 2: Créer et Appliquer les Migrations

```bash
# Créer les migrations pour l'app core
python manage.py makemigrations core

# Appliquer les migrations
python manage.py migrate core
```

## Étape 3: Appliquer les Permissions aux ViewSets

### Template pour un ViewSet Standard

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
    # Autres permissions selon les besoins
)

class MyViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    SoftDeleteMixin,  # Optionnel
    viewsets.ModelViewSet
):
    """Docstring avec les permissions documentées."""

    # Permissions par action
    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsAdmin],
    }

    # Configuration audit
    audit_log_actions = ['create', 'update', 'destroy']
    audit_log_changes = True

    # Configuration filtrage
    filter_field = 'created_by'  # ou autre champ approprié

    def get_queryset_for_teacher(self, queryset):
        """Filtrage personnalisé pour les enseignants."""
        return queryset.filter(teacher=self.request.user)
```

## Étape 4: Permissions par App

### Students App

**Permissions recommandées:**
- **list/retrieve**: `IsPedagogicalOrAbove` (tous peuvent voir)
- **create/update**: `IsTeacherOrAdmin` (enseignants gèrent leurs étudiants)
- **destroy**: `IsAdmin` (seuls admins peuvent supprimer)
- **predictions**: `CanViewPredictions`
- **export**: `IsPedagogicalOrAbove` + `DataExportThrottle`

**Filtrage:**
- Teachers: voir seulement leurs étudiants
- Pedagogical/DS/Admin: voir tous les étudiants

### Grades App

**Permissions recommandées:**
- **list/retrieve**: `IsPedagogicalOrAbove`
- **create/update**: `IsTeacherOrAdmin`
- **destroy**: `IsAdmin`

**Filtrage:**
- Teachers: voir seulement les notes de leurs étudiants
- Pedagogical/DS/Admin: voir toutes les notes

### Attendance App

**Permissions recommandées:**
- **list/retrieve**: `IsPedagogicalOrAbove`
- **create/update**: `IsTeacherOrAdmin`
- **destroy**: `IsAdmin`

**Filtrage:**
- Teachers: gérer seulement l'assiduité de leurs étudiants
- Pedagogical/DS/Admin: voir toute l'assiduité

### Predictions App

**Permissions recommandées:**
- **list/retrieve**: `CanViewPredictions`
- **create**: `CanRunMLPredictions` (Admin/DS seulement)
- **update/destroy**: `IsAdmin`

**Throttling:**
- Utiliser `MLPredictionThrottle` pour les opérations de prédiction

### Alerts App

**Permissions recommandées:**
- **list/retrieve**: `IsPedagogicalOrAbove`
- **create/update**: `CanManageAlerts`
- **destroy**: `IsAdmin`

**Filtrage:**
- Teachers: gérer seulement les alertes de leurs étudiants
- Pedagogical: voir toutes les alertes (lecture seule)
- DS/Admin: gérer toutes les alertes

### Programs App

**Permissions recommandées:**
- **list/retrieve**: `IsAuthenticated` (tous peuvent voir)
- **create/update/destroy**: `IsDSOrAdmin`

### Sessions App

**Permissions recommandées:**
- **list/retrieve**: `IsAuthenticated`
- **create/update/destroy**: `IsDSOrAdmin`

### ML App

**Permissions recommandées:**
- **run_training**: `CanRunMLPredictions` (Admin/DS)
- **view_models**: `IsPedagogicalOrAbove`

**Throttling:**
- `MLPredictionThrottle` pour toutes les opérations ML

## Étape 5: Exemples d'Implémentation

### Exemple 1: ViewSet Simple (Programs)

```python
from apps.core.mixins import RoleBasedPermissionMixin, AuditLogMixin
from apps.core.permissions import IsAuthenticated, IsDSOrAdmin

class ProgramViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    viewsets.ModelViewSet
):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsDSOrAdmin],
        'update': [IsDSOrAdmin],
        'partial_update': [IsDSOrAdmin],
        'destroy': [IsDSOrAdmin],
    }

    audit_log_actions = ['create', 'update', 'destroy']
```

### Exemple 2: ViewSet avec Filtrage (Grades)

```python
from apps.core.mixins import (
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin
)
from apps.core.permissions import IsPedagogicalOrAbove, IsTeacherOrAdmin

class GradeViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    viewsets.ModelViewSet
):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsAdmin],
    }

    audit_log_actions = ['create', 'update', 'destroy']

    def get_queryset_for_teacher(self, queryset):
        """Teachers see only grades for their students."""
        # Get all students taught by this teacher
        teacher_students = Student.objects.filter(
            teacher=self.request.user
        )
        return queryset.filter(student__in=teacher_students)
```

### Exemple 3: ViewSet avec Action Personnalisée et Throttling

```python
from apps.core.mixins import RoleBasedPermissionMixin, AuditLogMixin
from apps.core.permissions import IsPedagogicalOrAbove, CanRunMLPredictions
from apps.core.throttling import MLPredictionThrottle

class PredictionViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    viewsets.ModelViewSet
):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer

    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [CanRunMLPredictions],
        'run_batch_prediction': [CanRunMLPredictions],
    }

    audit_log_actions = ['create', 'run_batch_prediction']

    @action(
        detail=False,
        methods=['post'],
        throttle_classes=[MLPredictionThrottle]
    )
    def run_batch_prediction(self, request):
        """Run predictions for multiple students."""
        # Implementation
        pass
```

## Étape 6: Tester les Permissions

### Tests Manuels

```bash
# 1. Créer des utilisateurs de test avec différents rôles
python manage.py shell
```

```python
from apps.users.models import User

# Admin
admin = User.objects.create_user(
    email='admin@test.com',
    password='test123',
    first_name='Admin',
    last_name='User',
    role=User.Role.ADMIN
)

# DS
ds = User.objects.create_user(
    email='ds@test.com',
    password='test123',
    first_name='DS',
    last_name='User',
    role=User.Role.DS
)

# Pedagogical
pedagogical = User.objects.create_user(
    email='pedagogical@test.com',
    password='test123',
    first_name='Pedagogical',
    last_name='User',
    role=User.Role.PEDAGOGICAL
)

# Teacher
teacher = User.objects.create_user(
    email='teacher@test.com',
    password='test123',
    first_name='Teacher',
    last_name='User',
    role=User.Role.TEACHER
)
```

### Tests Automatisés

Créer `tests/test_permissions.py` dans chaque app:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User

class StudentPermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='test123',
            role=User.Role.ADMIN
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com',
            password='test123',
            role=User.Role.TEACHER
        )

    def test_admin_can_create_student(self):
        """Test that admin can create students."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/students/', {
            'matricule': '12345',
            'first_name': 'John',
            'last_name': 'Doe',
            # ... other fields
        })
        self.assertEqual(response.status_code, 201)

    def test_teacher_can_create_student(self):
        """Test that teacher can create students."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/students/', {
            'matricule': '12345',
            'first_name': 'John',
            'last_name': 'Doe',
            # ... other fields
        })
        self.assertEqual(response.status_code, 201)
```

## Étape 7: Vérifier l'Audit Log

Accéder à l'admin Django pour voir les logs d'audit:

```
http://localhost:8000/admin/core/auditlog/
```

Filtrer par:
- Utilisateur
- Action
- Modèle
- Date

## Étape 8: Monitorer les Rate Limits

Les rate limits sont automatiquement appliqués. Pour tester:

```python
# Script pour tester les rate limits
import requests

url = 'http://localhost:8000/api/students/'
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

# Faire 100 requêtes rapides
for i in range(100):
    response = requests.get(url, headers=headers)
    print(f"Request {i+1}: {response.status_code}")

# Devrait recevoir 429 (Too Many Requests) après la limite
```

## Checklist de Sécurité

- [ ] App core installée dans INSTALLED_APPS
- [ ] Middleware de sécurité activés
- [ ] Migrations appliquées
- [ ] Permissions appliquées à tous les ViewSets
- [ ] Audit logging configuré
- [ ] Rate limiting configuré
- [ ] Tests de permissions écrits
- [ ] Documentation mise à jour
- [ ] Rôles utilisateurs configurés
- [ ] Accès admin configuré pour voir les logs

## Dépannage

### Problème: Circular imports

**Solution**: Importer les modèles/serializers dans les méthodes plutôt qu'au niveau du module.

```python
# Au lieu de:
from apps.predictions.models import Prediction

# Faire:
def predictions(self, request, pk=None):
    from apps.predictions.models import Prediction
    # ...
```

### Problème: Permission denied pour tous

**Solution**: Vérifier que l'utilisateur a le bon rôle et que les permissions sont correctement configurées.

```python
# Debug dans le shell
user = User.objects.get(email='test@test.com')
print(user.role)  # Vérifier le rôle
print(user.is_teacher())  # Tester les méthodes
```

### Problème: Middleware ne fonctionne pas

**Solution**: Vérifier l'ordre des middleware dans settings.py. Les middleware custom doivent être après AuthenticationMiddleware.

### Problème: Rate limit trop restrictif

**Solution**: Ajuster les rates dans settings.py `DEFAULT_THROTTLE_RATES`.

## Ressources

- Documentation Core App: `backend/apps/core/README.md`
- Exemple complet: `backend/apps/students/views_with_permissions.py`
- Tests: `backend/apps/core/tests/`

## Support

Pour toute question sur l'implémentation du système de sécurité, consulter:
1. Ce guide
2. Le README de l'app core
3. Les tests existants
4. L'exemple dans students/views_with_permissions.py
