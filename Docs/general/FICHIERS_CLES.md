# SPAS - Fichiers Clés de l'API REST

## Configuration Principale

### C:/Users/Public/Libraries/one/SPAS/backend/config/settings.py
Configuration Django et DRF avec:
- REST_FRAMEWORK settings
- SIMPLE_JWT configuration
- SPECTACULAR_SETTINGS pour documentation
- Pagination: 20 items/page
- Authentication: JWT

### C:/Users/Public/Libraries/one/SPAS/backend/config/urls.py
Routes principales:
- /admin/ - Interface d'administration
- /api/schema/ - Schéma OpenAPI
- /api/docs/ - Documentation Swagger
- /api/redoc/ - Documentation ReDoc
- /api/auth/ - Authentification
- /api/users/ - Utilisateurs
- /api/students/ - Étudiants
- /api/programs/ - Programmes
- /api/sessions/ - Sessions
- /api/grades/ - Notes
- /api/attendance/ - Présences
- /api/ml/ - Modèles ML
- /api/predictions/ - Prédictions
- /api/alerts/ - Alertes

---

## Apps et Fichiers

### 1. Authentication
**Chemin:** backend/apps/authentication/

**Fichiers clés:**
- views.py: RegisterView, LoginView, LogoutView, RefreshView
- serializers.py: RegisterSerializer, LoginSerializer
- urls.py: Configuration des routes

---

### 2. Users
**Chemin:** backend/apps/users/

**Fichiers:**
- models.py: User (custom model)
- serializers.py: UserSerializer, ChangePasswordSerializer
- views.py: UserViewSet
- urls.py: Configuration Router
- permissions.py (si nécessaire): Custom permissions

**ViewSet:** UserViewSet
**Actions:** list, create, retrieve, update, destroy, me, change_password, activate, deactivate

---

### 3. Students
**Chemin:** backend/apps/students/

**Fichiers:**
- models.py: Student
- serializers.py: StudentSerializer, StudentListSerializer
- views.py: StudentViewSet
- urls.py: Configuration Router

**ViewSet:** StudentViewSet
**Actions:** list, create, retrieve, update, destroy, predictions, grades, attendance, at_risk

---

### 4. Programs
**Chemin:** backend/apps/programs/

**Fichiers:**
- models.py: Program, Subject
- serializers.py: ProgramSerializer, SubjectSerializer
- views.py: ProgramViewSet, SubjectViewSet
- urls.py: Configuration Router (2 viewsets)

**ViewSets:** 
- ProgramViewSet: list, create, retrieve, update, destroy, students, subjects
- SubjectViewSet: list, create, retrieve, update, destroy

---

### 5. Sessions
**Chemin:** backend/apps/sessions/

**Fichiers:**
- models.py: Session
- serializers.py: SessionSerializer
- views.py: SessionViewSet
- urls.py: Configuration Router

**ViewSet:** SessionViewSet
**Actions:** list, create, retrieve, update, destroy, students, active (à ajouter)

---

### 6. Grades
**Chemin:** backend/apps/grades/

**Fichiers:**
- models.py: Grade
- serializers.py: GradeSerializer
- views.py: GradeViewSet
- urls.py: Configuration Router

**ViewSet:** GradeViewSet
**Actions:** list, create, retrieve, update, destroy, student_grades, bulk_create, statistics, by_student (à ajouter), by_subject (à ajouter)

---

### 7. Attendance
**Chemin:** backend/apps/attendance/

**Fichiers:**
- models.py: Attendance
- serializers.py: AttendanceSerializer
- views.py: AttendanceViewSet
- urls.py: Configuration Router

**ViewSet:** AttendanceViewSet
**Actions:** list, create, retrieve, update, destroy, student_attendance, bulk_create, statistics, low_attendance, by_date_range (à ajouter)

---

### 8. ML Models
**Chemin:** backend/apps/ml/

**Fichiers:**
- models.py: MLModel, TrainingJob
- serializers.py: MLModelSerializer, TrainingJobSerializer
- views.py: MLModelViewSet, TrainingJobViewSet
- urls.py: Configuration Router (2 viewsets)
- tasks.py (optionnel): Celery tasks pour entraînement

**ViewSets:**
- MLModelViewSet: list, create, retrieve, update, destroy, activate, train, active (à ajouter)
- TrainingJobViewSet: list, retrieve (ReadOnly)

---

### 9. Predictions
**Chemin:** backend/apps/predictions/

**Fichiers:**
- models.py: Prediction, RecommendedIntervention
- serializers.py: PredictionSerializer, RecommendedInterventionSerializer
- views.py: PredictionViewSet, RecommendedInterventionViewSet
- urls.py: Configuration Router (2 viewsets)
- tasks.py (optionnel): Celery tasks pour génération

**ViewSets:**
- PredictionViewSet: list, create, retrieve, update, destroy, at_risk, statistics, generate_bulk, add_intervention, recent (à ajouter), by_risk_level (à ajouter), accuracy_metrics (à ajouter)
- RecommendedInterventionViewSet: list, create, retrieve, update, destroy

---

### 10. Alerts
**Chemin:** backend/apps/alerts/

**Fichiers:**
- models.py: Alert, AlertAction
- serializers.py: AlertSerializer, AlertActionSerializer
- views.py: AlertViewSet, AlertActionViewSet
- urls.py: Configuration Router (2 viewsets)

**ViewSets:**
- AlertViewSet: list, create, retrieve, update, destroy, my_alerts, active, critical, acknowledge, resolve, dismiss, assign, statistics, unread (à ajouter), by_level (à ajouter)
- AlertActionViewSet: list, create, retrieve

---

## Résumé des Routes

```
/api/auth/
  POST /register/
  POST /login/
  POST /refresh/
  POST /logout/

/api/users/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /me/
  POST /{id}/change-password/
  POST /{id}/activate/
  POST /{id}/deactivate/

/api/students/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /{id}/predictions/
  GET /{id}/grades/
  GET /{id}/attendance/
  GET /at-risk/

/api/programs/
  GET / (list programs)
  POST / (create program)
  GET /{id}/ (retrieve program)
  PUT/PATCH /{id}/ (update program)
  DELETE /{id}/ (destroy program)
  GET /{id}/students/
  GET /{id}/subjects/ (à ajouter)

/api/subjects/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)

/api/sessions/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /{id}/students/
  GET /active/ (à ajouter)

/api/grades/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /student/{student_id}/
  POST /bulk-create/
  GET /statistics/
  GET /by-student/ (à ajouter)
  GET /by-subject/ (à ajouter)

/api/attendance/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /student/{student_id}/
  POST /bulk-create/
  GET /statistics/
  GET /low-attendance/
  GET /by-date-range/ (à ajouter)

/api/ml/
  GET / (list models)
  POST / (create model)
  GET /{id}/ (retrieve model)
  PUT/PATCH /{id}/ (update model)
  DELETE /{id}/ (destroy model)
  POST /{id}/activate/
  POST /{id}/train/
  GET /active/ (à ajouter)

/api/ml/training-jobs/
  GET / (list)
  GET /{id}/ (retrieve)

/api/predictions/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /at-risk/
  GET /statistics/
  POST /generate-bulk/
  POST /{id}/add-intervention/
  GET /recent/ (à ajouter)
  GET /by-risk-level/ (à ajouter)
  GET /accuracy-metrics/ (à ajouter)

/api/predictions/interventions/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)

/api/alerts/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
  PUT/PATCH /{id}/ (update)
  DELETE /{id}/ (destroy)
  GET /my-alerts/
  GET /active/
  GET /critical/
  POST /{id}/acknowledge/
  POST /{id}/resolve/
  POST /{id}/dismiss/
  POST /{id}/assign/
  GET /statistics/
  GET /unread/ (à ajouter)
  GET /by-level/ (à ajouter)

/api/alerts/actions/
  GET / (list)
  POST / (create)
  GET /{id}/ (retrieve)
```

---

## Documentation API

**Accès:**
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema JSON: http://localhost:8000/api/schema/

