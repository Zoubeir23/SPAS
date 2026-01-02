# SPAS - Récapitulatif Complet de l'API REST

## État Actuel du Projet

### Apps Complètes avec ViewSets

#### 1. Students (COMPLET)
**Fichiers:**
- models.py: Student
- serializers.py: StudentSerializer, StudentListSerializer
- views.py: StudentViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/students/
- GET /api/students/{id}/
- GET /api/students/{id}/predictions/
- GET /api/students/{id}/grades/
- GET /api/students/{id}/attendance/
- GET /api/students/at-risk/

#### 2. Programs (COMPLET)
**Fichiers:**
- models.py: Program, Subject
- serializers.py: ProgramSerializer, SubjectSerializer
- views.py: ProgramViewSet, SubjectViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/programs/
- GET /api/programs/{id}/students/
- GET /api/subjects/

#### 3. Sessions (COMPLET)
**Fichiers:**
- models.py: Session
- serializers.py: SessionSerializer
- views.py: SessionViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/sessions/
- GET /api/sessions/{id}/students/

#### 4. Grades (COMPLET)
**Fichiers:**
- models.py: Grade
- serializers.py: GradeSerializer
- views.py: GradeViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/grades/
- POST /api/grades/bulk-create/
- GET /api/grades/statistics/
- GET /api/grades/student/{student_id}/

#### 5. Attendance (COMPLET)
**Fichiers:**
- models.py: Attendance
- serializers.py: AttendanceSerializer
- views.py: AttendanceViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/attendance/
- POST /api/attendance/bulk-create/
- GET /api/attendance/statistics/
- GET /api/attendance/low-attendance/
- GET /api/attendance/student/{student_id}/

#### 6. Predictions (COMPLET)
**Fichiers:**
- models.py: Prediction, RecommendedIntervention
- serializers.py: PredictionSerializer, RecommendedInterventionSerializer
- views.py: PredictionViewSet, RecommendedInterventionViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/predictions/
- GET /api/predictions/at-risk/
- GET /api/predictions/statistics/
- POST /api/predictions/generate-bulk/

#### 7. Alerts (COMPLET)
**Fichiers:**
- models.py: Alert, AlertAction
- serializers.py: AlertSerializer, AlertActionSerializer
- views.py: AlertViewSet, AlertActionViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/alerts/
- GET /api/alerts/my-alerts/
- GET /api/alerts/active/
- GET /api/alerts/critical/
- POST /api/alerts/{id}/acknowledge/
- POST /api/alerts/{id}/resolve/
- POST /api/alerts/{id}/dismiss/
- POST /api/alerts/{id}/assign/
- GET /api/alerts/statistics/

#### 8. ML Models (COMPLET)
**Fichiers:**
- models.py: MLModel, TrainingJob
- serializers.py: MLModelSerializer, TrainingJobSerializer
- views.py: MLModelViewSet, TrainingJobViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/ml/
- POST /api/ml/{id}/activate/
- POST /api/ml/{id}/train/

#### 9. Users (COMPLET)
**Fichiers:**
- models.py: User
- serializers.py: UserSerializer, ChangePasswordSerializer
- views.py: UserViewSet
- urls.py: Configuration Router

**Endpoints:**
- GET /api/users/
- GET /api/users/me/
- POST /api/users/{id}/change-password/
- POST /api/users/{id}/activate/
- POST /api/users/{id}/deactivate/

#### 10. Authentication (COMPLET)
**Endpoints:**
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/refresh/
- POST /api/auth/logout/

---

## Actions Personnalisées Recommandées à Ajouter

### Sessions
```python
@action(detail=False, methods=['get'])
def active(self, request):
    # Retourner la session actuellement active
```

### Programs
```python
@action(detail=True, methods=['get'])
def subjects(self, request, pk=None):
    # Liste des matières du programme
```

### Grades
```python
@action(detail=False, methods=['get'])
def by_student(self, request):
    # Notes groupées par étudiant

@action(detail=False, methods=['get'])
def by_subject(self, request):
    # Notes groupées par matière
```

### Attendance
```python
@action(detail=False, methods=['get'])
def by_date_range(self, request):
    # Présences sur une période
```

### Predictions
```python
@action(detail=False, methods=['get'])
def recent(self, request):
    # Prédictions récentes (30 derniers jours)

@action(detail=False, methods=['get'])
def by_risk_level(self, request):
    # Prédictions par niveau de risque

@action(detail=False, methods=['get'])
def accuracy_metrics(self, request):
    # Métriques de précision
```

### Alerts
```python
@action(detail=False, methods=['get'])
def unread(self, request):
    # Alertes non lues

@action(detail=False, methods=['get'])
def by_level(self, request):
    # Alertes par niveau de sévérité
```

### ML Models
```python
@action(detail=False, methods=['get'])
def active(self, request):
    # Modèles actifs
```

---

## Configuration Globale

### Pagination
- Par défaut: 20 items/page
- Configuré dans settings.py

### Authentification
- JWT avec SimpleJWT
- Access token: 60 minutes
- Refresh token: 1 jour

### Permissions
- IsAuthenticated par défaut
- IsAdminUser pour actions sensibles

### Documentation API
- Swagger UI: /api/docs/
- ReDoc: /api/redoc/
- Schema: /api/schema/

---

## Structure des URLs

```
/api/
  /auth/
    /register/
    /login/
    /refresh/
    /logout/
  /users/
  /students/
  /programs/
  /sessions/
  /grades/
  /attendance/
  /ml/
  /predictions/
  /alerts/
  /docs/
  /redoc/
  /schema/
```

---

## Filtres et Recherche

### Students
- Filtres: program, session, risk_level, status
- Recherche: matricule, first_name, last_name, email
- Tri: last_name, first_name, created_at, risk_score

### Programs
- Filtres: status
- Recherche: name, code
- Tri: code, name, created_at

### Sessions
- Filtres: status, year
- Recherche: name, year
- Tri: year, start_date, created_at

### Grades
- Filtres: student, subject, session, type
- Recherche: student__first_name, student__last_name
- Tri: date, value, created_at

### Attendance
- Filtres: student, subject, status, date
- Recherche: student__first_name, student__last_name
- Tri: date, created_at

### Predictions
- Filtres: student, risk_level, is_at_risk, is_latest, period
- Tri: risk_score, predicted_at, confidence

### Alerts
- Filtres: student, alert_type, severity, status, assigned_to
- Recherche: student__student_id, student__first_name, title
- Tri: created_at, severity, status

### ML Models
- Filtres: model_type, is_active
- Tri: created_at, accuracy

### Users
- Filtres: role, is_active
- Recherche: email, first_name, last_name
- Tri: email, created_at, last_name

---

## Format de Réponse

### Liste Paginée
```json
{
  "count": 100,
  "next": "http://api/students/?page=2",
  "previous": null,
  "results": [...]
}
```

### Objet Simple
```json
{
  "id": 1,
  "field1": "value1",
  ...
}
```

### Succès avec Message
```json
{
  "success": true,
  "message": "Opération réussie",
  "data": {...}
}
```

### Erreur
```json
{
  "error": "Message d'erreur",
  "details": {...}
}
```

