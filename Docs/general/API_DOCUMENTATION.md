# SPAS - Documentation API REST Complète

## Apps et Endpoints

### 1. Students
- GET /api/students/ - Liste
- POST /api/students/ - Créer
- GET /api/students/{id}/ - Détails
- GET /api/students/{id}/predictions/ - Prédictions
- GET /api/students/{id}/grades/ - Notes
- GET /api/students/{id}/attendance/ - Présences  
- GET /api/students/at-risk/ - À risque

### 2. Programs
- GET /api/programs/ - Liste
- GET /api/programs/{id}/students/ - Étudiants
- GET /api/subjects/ - Matières

### 3. Sessions
- GET /api/sessions/ - Liste
- GET /api/sessions/{id}/students/ - Étudiants
- GET /api/sessions/active/ - Active

### 4. Grades
- GET /api/grades/ - Liste
- POST /api/grades/bulk-create/ - Créer plusieurs
- GET /api/grades/statistics/ - Statistiques

### 5. Attendance
- GET /api/attendance/ - Liste
- POST /api/attendance/bulk-create/ - Créer plusieurs
- GET /api/attendance/statistics/ - Statistiques
- GET /api/attendance/low-attendance/ - Faible présence

### 6. Predictions
- GET /api/predictions/ - Liste
- GET /api/predictions/at-risk/ - À risque
- GET /api/predictions/statistics/ - Statistiques
- POST /api/predictions/generate-bulk/ - Générer en masse

### 7. Alerts
- GET /api/alerts/ - Liste
- GET /api/alerts/active/ - Actives
- GET /api/alerts/critical/ - Critiques
- POST /api/alerts/{id}/acknowledge/ - Accuser réception
- POST /api/alerts/{id}/resolve/ - Résoudre
- GET /api/alerts/statistics/ - Statistiques

### 8. ML Models
- GET /api/ml-models/ - Liste
- POST /api/ml-models/{id}/activate/ - Activer
- POST /api/ml-models/{id}/train/ - Entraîner

### 9. Users  
- GET /api/users/ - Liste
- GET /api/users/me/ - Mon profil
- POST /api/users/{id}/change-password/ - Changer mot de passe

## Authentification
- POST /api/auth/register/ - Inscription
- POST /api/auth/login/ - Connexion
- POST /api/auth/refresh/ - Rafraîchir token
- POST /api/auth/logout/ - Déconnexion

