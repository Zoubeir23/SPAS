# Core App - Système de Permissions et Sécurité SPAS

## Vue d'ensemble

L'app `core` fournit un système complet de permissions, d'audit et de sécurité pour SPAS. Elle inclut :

- **Permissions personnalisées** basées sur les rôles (ADMIN, DS, PEDAGOGICAL, TEACHER)
- **Audit logging** automatique de toutes les actions importantes
- **Rate limiting** par rôle utilisateur
- **Soft deletion** pour maintenir l'intégrité des données
- **Middleware de sécurité** pour protéger l'application

## Structure

```
apps/core/
├── __init__.py
├── admin.py              # Configuration admin pour AuditLog
├── apps.py               # Configuration de l'app
├── middleware.py         # Middleware de sécurité et d'audit
├── mixins.py             # Mixins réutilisables pour ViewSets
├── models.py             # Modèles AuditLog et SoftDeleteModel
├── permissions.py        # Classes de permissions personnalisées
├── throttling.py         # Classes de rate limiting
├── utils.py              # Fonctions utilitaires
└── tests/
    ├── __init__.py
    ├── test_permissions.py
    └── test_models.py
```

## Permissions Disponibles

### 1. IsAdmin
Seuls les administrateurs peuvent accéder.

```python
from apps.core.permissions import IsAdmin

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
```

### 2. IsTeacherOrAdmin
Enseignants et administrateurs.

```python
from apps.core.permissions import IsTeacherOrAdmin

class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
```

### 3. IsDSOrAdmin
Directeurs des Études et administrateurs.

```python
from apps.core.permissions import IsDSOrAdmin

class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDSOrAdmin]
```

### 4. IsPedagogicalOrAbove
Conseillers pédagogiques, DS et administrateurs.

```python
from apps.core.permissions import IsPedagogicalOrAbove

class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsPedagogicalOrAbove]
```

### 5. CanManageStudents
Peut gérer les étudiants (avec restrictions au niveau objet).

```python
from apps.core.permissions import CanManageStudents

class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanManageStudents]
```

### 6. CanViewPredictions
Peut voir les prédictions ML.

```python
from apps.core.permissions import CanViewPredictions

class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, CanViewPredictions]
```

### 7. CanManageAlerts
Peut gérer les alertes.

```python
from apps.core.permissions import CanManageAlerts

class AlertViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanManageAlerts]
```

### 8. CanRunMLPredictions
Peut lancer des prédictions ML (ADMIN et DS uniquement).

```python
from apps.core.permissions import CanRunMLPredictions

@action(detail=False, methods=['post'])
def run_prediction(self, request):
    # Lance la prédiction ML
    pass
```

## Utilisation des Mixins

### RoleBasedPermissionMixin
Applique différentes permissions selon l'action.

```python
from apps.core.mixins import RoleBasedPermissionMixin
from apps.core.permissions import IsAdmin, IsTeacherOrAdmin, IsPedagogicalOrAbove

class StudentViewSet(RoleBasedPermissionMixin, viewsets.ModelViewSet):
    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsAdmin],
    }
```

### AuditLogMixin
Journalise automatiquement les actions.

```python
from apps.core.mixins import AuditLogMixin

class StudentViewSet(AuditLogMixin, viewsets.ModelViewSet):
    # Journalise create, update, destroy
    audit_log_actions = ['create', 'update', 'destroy']

    # Ou journalise toutes les actions
    audit_log_all = True

    # Inclure les détails des changements
    audit_log_changes = True
```

### QuerySetFilterMixin
Filtre les querysets selon le rôle.

```python
from apps.core.mixins import QuerySetFilterMixin

class StudentViewSet(QuerySetFilterMixin, viewsets.ModelViewSet):
    queryset = Student.objects.all()
    filter_field = 'teacher'  # Les enseignants voient leurs étudiants

    # Personnaliser le filtrage
    def get_queryset_for_teacher(self, queryset):
        # Logique personnalisée pour les enseignants
        return queryset.filter(teacher=self.request.user)
```

### SoftDeleteMixin
Implémente la suppression logique.

```python
from apps.core.mixins import SoftDeleteMixin

class StudentViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    # destroy() fera une suppression logique
    # Actions disponibles:
    # - DELETE /api/students/1/ (soft delete)
    # - POST /api/students/1/restore/ (restaurer)
    # - DELETE /api/students/1/hard-delete/ (suppression permanente)
```

## Exemple Complet d'un ViewSet

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

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
from apps.core.throttling import DataExportThrottle

from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    SoftDeleteMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet for managing students with role-based permissions.

    Permissions:
    - list/retrieve: Pedagogical and above
    - create/update: Teachers and admins
    - destroy: Admin only
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_field = 'teacher'

    # Permissions par action
    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsAdmin],
        'export': [IsPedagogicalOrAbove],
    }

    # Audit logging
    audit_log_actions = ['create', 'update', 'destroy', 'export']
    audit_log_changes = True

    @action(
        detail=False,
        methods=['get'],
        throttle_classes=[DataExportThrottle]
    )
    def export(self, request):
        """Export students to CSV."""
        # Logique d'export
        return Response({'status': 'exported'})

    def get_queryset_for_teacher(self, queryset):
        """Teachers see only their students."""
        return queryset.filter(teacher=self.request.user)
```

## Rate Limiting (Throttling)

### Classes de Throttling Disponibles

```python
from apps.core.throttling import (
    BurstRateThrottle,          # 60/min - Prévient les rafales
    SustainedRateThrottle,      # 1000/hour - Limite globale
    MLPredictionThrottle,       # Limite pour ML
    DataExportThrottle,         # Limite pour exports
    StrictAnonRateThrottle,     # 20/hour pour anonymes
)

class MyViewSet(viewsets.ModelViewSet):
    throttle_classes = [MLPredictionThrottle]
```

### Limites par Rôle

Les limites sont automatiquement appliquées selon le rôle :

- **ADMIN**: 10000 req/hour
- **DS**: 5000 req/hour
- **PEDAGOGICAL**: 3000 req/hour
- **TEACHER**: 2000 req/hour
- **Anonymous**: 20 req/hour

## Modèles

### AuditLog

Journalise toutes les actions importantes.

```python
from apps.core.models import AuditLog

# Créer manuellement un log d'audit
AuditLog.log_action(
    user=request.user,
    action=AuditLog.Action.CREATE,
    content_object=student,
    changes={'name': 'John Doe'},
    ip_address=get_client_ip(request),
    endpoint='/api/students/',
    method='POST'
)
```

### SoftDeleteModel

Modèle abstrait pour la suppression logique.

```python
from apps.core.models import SoftDeleteModel

class Student(SoftDeleteModel):
    name = models.CharField(max_length=100)
    # ... autres champs

# Utilisation
student = Student.objects.get(id=1)
student.delete(user=request.user)  # Suppression logique

# Requêtes
Student.objects.all()  # Seulement les actifs
Student.objects.all_with_deleted()  # Tous
Student.objects.deleted_only()  # Seulement les supprimés

# Restaurer
student.restore()

# Suppression permanente
student.hard_delete()
```

## Middleware

Les middleware suivants sont activés :

1. **SecurityHeadersMiddleware** - Ajoute les en-têtes de sécurité
2. **AuditMiddleware** - Journalise les requêtes importantes
3. **PermissionDeniedLoggingMiddleware** - Journalise les accès refusés
4. **RequestLoggingMiddleware** (DEBUG uniquement) - Journalise toutes les requêtes

## Tests

Lancer les tests de permissions :

```bash
python manage.py test apps.core.tests.test_permissions
python manage.py test apps.core.tests.test_models
```

## Migration

Créer et appliquer les migrations :

```bash
python manage.py makemigrations core
python manage.py migrate core
```

## Bonnes Pratiques

1. **Toujours utiliser RoleBasedPermissionMixin** pour des permissions par action
2. **Activer AuditLogMixin** pour les opérations sensibles
3. **Utiliser SoftDeleteModel** pour maintenir l'intégrité référentielle
4. **Appliquer QuerySetFilterMixin** pour filtrer automatiquement par rôle
5. **Définir des throttle_classes** pour les opérations coûteuses
6. **Documenter les permissions** dans les docstrings des ViewSets

## Configuration dans settings.py

Le système est configuré dans `config/settings.py` :

```python
INSTALLED_APPS = [
    # ...
    'apps.core',  # Doit être avant les autres apps locales
    # ...
]

MIDDLEWARE = [
    # ...
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.AuditMiddleware',
    'apps.core.middleware.PermissionDeniedLoggingMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'apps.core.throttling.BurstRateThrottle',
        'apps.core.throttling.SustainedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'burst': '60/min',
        'sustained': '1000/hour',
        # ... autres limites
    },
}
```
