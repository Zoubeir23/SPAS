# ViewSets et Actions Personnalisées - SPAS API

## 1. StudentViewSet

### Actions CRUD Standard
- list() - GET /api/students/
- create() - POST /api/students/
- retrieve() - GET /api/students/{id}/
- update() - PUT /api/students/{id}/
- partial_update() - PATCH /api/students/{id}/
- destroy() - DELETE /api/students/{id}/

### Actions Personnalisées
- predictions() - GET /api/students/{id}/predictions/
  - Récupère toutes les prédictions d'un étudiant
- grades() - GET /api/students/{id}/grades/
  - Récupère toutes les notes d'un étudiant
- attendance() - GET /api/students/{id}/attendance/
  - Récupère tous les enregistrements de présence
- at_risk() - GET /api/students/at-risk/
  - Liste des étudiants à risque (medium, high)

### Filtres
- program, session, risk_level, status

### Recherche
- matricule, first_name, last_name, email

---

## 2. ProgramViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- students() - GET /api/programs/{id}/students/
  - Liste des étudiants dans le programme
- subjects() - GET /api/programs/{id}/subjects/
  - Liste des matières du programme

### Filtres
- status

---

## 3. SubjectViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Filtres
- program (query param)

---

## 4. SessionViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- students() - GET /api/sessions/{id}/students/
  - Liste des étudiants dans la session
- active() - GET /api/sessions/active/
  - Récupère la session actuellement active

### Filtres
- status, year

---

## 5. GradeViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- student_grades() - GET /api/grades/student/{student_id}/
  - Notes d'un étudiant spécifique
- bulk_create() - POST /api/grades/bulk-create/
  - Créer plusieurs notes en une seule requête
- statistics() - GET /api/grades/statistics/
  - Statistiques globales des notes
- by_student() - GET /api/grades/by-student/
  - Notes groupées par étudiant
- by_subject() - GET /api/grades/by-subject/
  - Notes groupées par matière

### Filtres
- student, subject, session, type

---

## 6. AttendanceViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- student_attendance() - GET /api/attendance/student/{student_id}/
  - Présences d'un étudiant spécifique
- bulk_create() - POST /api/attendance/bulk-create/
  - Créer plusieurs enregistrements de présence
- statistics() - GET /api/attendance/statistics/
  - Statistiques de présence
- low_attendance() - GET /api/attendance/low-attendance/
  - Étudiants avec un taux de présence faible
- by_date_range() - GET /api/attendance/by-date-range/
  - Présences sur une période donnée

### Filtres
- student, subject, status, date

---

## 7. PredictionViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- at_risk() - GET /api/predictions/at-risk/
  - Prédictions indiquant un risque
- statistics() - GET /api/predictions/statistics/
  - Statistiques des prédictions
- generate_bulk() - POST /api/predictions/generate-bulk/
  - Générer des prédictions pour tous les étudiants actifs
- add_intervention() - POST /api/predictions/{id}/add-intervention/
  - Ajouter une intervention recommandée
- recent() - GET /api/predictions/recent/
  - Prédictions récentes
- by_risk_level() - GET /api/predictions/by-risk-level/
  - Prédictions par niveau de risque
- accuracy_metrics() - GET /api/predictions/accuracy-metrics/
  - Métriques de précision du modèle

### Filtres
- student, risk_level, is_at_risk, is_latest, period

---

## 8. AlertViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- my_alerts() - GET /api/alerts/my-alerts/
  - Alertes assignées à l'utilisateur connecté
- active() - GET /api/alerts/active/
  - Alertes actives
- critical() - GET /api/alerts/critical/
  - Alertes critiques
- acknowledge() - POST /api/alerts/{id}/acknowledge/
  - Accuser réception d'une alerte
- resolve() - POST /api/alerts/{id}/resolve/
  - Résoudre une alerte
- dismiss() - POST /api/alerts/{id}/dismiss/
  - Rejeter une alerte
- assign() - POST /api/alerts/{id}/assign/
  - Assigner une alerte à un utilisateur
- statistics() - GET /api/alerts/statistics/
  - Statistiques des alertes
- unread() - GET /api/alerts/unread/
  - Alertes non lues
- by_level() - GET /api/alerts/by-level/
  - Alertes par niveau de sévérité

### Filtres
- student, alert_type, severity, status, assigned_to

---

## 9. MLModelViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- activate() - POST /api/ml-models/{id}/activate/
  - Activer un modèle ML
- train() - POST /api/ml-models/{id}/train/
  - Lancer l'entraînement d'un modèle
- active() - GET /api/ml-models/active/
  - Modèles actuellement actifs

### Filtres
- model_type, is_active

---

## 10. UserViewSet

### Actions CRUD Standard
- list(), create(), retrieve(), update(), partial_update(), destroy()

### Actions Personnalisées
- me() - GET /api/users/me/
  - Profil de l'utilisateur connecté
- change_password() - POST /api/users/{id}/change-password/
  - Changer le mot de passe
- activate() - POST /api/users/{id}/activate/
  - Activer un compte utilisateur
- deactivate() - POST /api/users/{id}/deactivate/
  - Désactiver un compte utilisateur

### Filtres
- role, is_active

---

## Permissions Globales

### Par Rôle
- **ADMIN**: Accès complet (CRUD sur toutes les ressources)
- **TEACHER**: Lecture/écriture sur students, grades, attendance
- **DS**: Lecture sur toutes les ressources, écriture limitée
- **PEDAGOGICAL**: Lecture sur toutes les ressources, gestion des alertes

### Actions Protégées (Admin uniquement)
- ML Model: create, update, destroy, train
- User: create, update, destroy (sauf son propre profil)

---

## Configuration

### Pagination
- Par défaut: 20 items par page
- Paramètre: ?page=2

### Tri
- Paramètre: ?ordering=-created_at
- Paramètre: ?ordering=last_name,first_name

### Recherche
- Paramètre: ?search=john

### Filtres
- Paramètres: ?status=active&risk_level=high

