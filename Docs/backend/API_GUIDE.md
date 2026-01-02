# SPAS API - Guide Complet

## Table des Matières
1. [Authentification](#authentification)
2. [Format des Réponses](#format-des-réponses)
3. [Endpoints par Module](#endpoints-par-module)
4. [Exemples d'Utilisation](#exemples-dutilisation)
5. [Codes d'Erreur](#codes-derreur)

## Authentification

SPAS utilise JWT (JSON Web Tokens) pour l'authentification.

### Obtenir un Token

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "admin@spas.ca",
  "password": "admin123"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Utiliser le Token

Incluez le token d'accès dans le header Authorization:

```http
GET /api/students/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Rafraîchir le Token

```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Format des Réponses

### Réponse de Succès

```json
{
  "id": 1,
  "student_id": "2024001",
  "first_name": "Alexandre",
  "last_name": "Tremblay",
  "email": "alexandre.tremblay@student.spas.ca",
  "status": "ACTIVE"
}
```

### Réponse avec Pagination

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/students/?page=2",
  "previous": null,
  "results": [...]
}
```

### Réponse d'Erreur

```json
{
  "success": false,
  "error": {
    "message": "Student not found.",
    "status_code": 404,
    "details": {...}
  }
}
```

## Endpoints par Module

### 1. Utilisateurs (`/api/users/`)

#### Lister les utilisateurs
```http
GET /api/users/
Authorization: Bearer {token}
```

#### Profil utilisateur actuel
```http
GET /api/users/me/
Authorization: Bearer {token}
```

#### Modifier le profil
```http
PUT /api/users/update_profile/
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Jean",
  "last_name": "Dupont",
  "phone": "514-123-4567"
}
```

#### Changer le mot de passe
```http
POST /api/users/change_password/
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "ancien123",
  "new_password": "nouveau123",
  "new_password_confirm": "nouveau123"
}
```

### 2. Étudiants (`/api/students/`)

#### Lister les étudiants
```http
GET /api/students/
Authorization: Bearer {token}

# Avec filtres
GET /api/students/?status=ACTIVE&program=1
GET /api/students/?search=Alexandre
```

#### Créer un étudiant
```http
POST /api/students/
Authorization: Bearer {token}
Content-Type: application/json

{
  "student_id": "2024009",
  "first_name": "Nouveau",
  "last_name": "Étudiant",
  "email": "nouveau.etudiant@student.spas.ca",
  "program": 1,
  "admission_date": "2024-08-15",
  "phone": "514-123-4567"
}
```

#### Détails d'un étudiant
```http
GET /api/students/{id}/
Authorization: Bearer {token}
```

#### Étudiants à risque
```http
GET /api/students/at_risk/
Authorization: Bearer {token}
```

#### Changer le statut
```http
POST /api/students/{id}/change_status/
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "DROPPED"
}
```

### 3. Programmes (`/api/programs/`)

#### Lister les programmes
```http
GET /api/programs/programs/
Authorization: Bearer {token}

# Programmes actifs seulement
GET /api/programs/programs/?is_active=true
```

#### Cours d'un programme
```http
GET /api/programs/programs/{id}/courses/
Authorization: Bearer {token}
```

#### Étudiants d'un programme
```http
GET /api/programs/programs/{id}/students/
Authorization: Bearer {token}
```

#### Lister les cours
```http
GET /api/programs/courses/
Authorization: Bearer {token}

# Cours d'un programme spécifique
GET /api/programs/courses/?program=1
GET /api/programs/courses/?is_mandatory=true
```

### 4. Sessions (`/api/sessions/`)

#### Périodes académiques
```http
GET /api/sessions/periods/
Authorization: Bearer {token}
```

#### Période actuelle
```http
GET /api/sessions/periods/current/
Authorization: Bearer {token}
```

#### Sessions de cours
```http
GET /api/sessions/course-sessions/
Authorization: Bearer {token}

# Filtres
GET /api/sessions/course-sessions/?period=1
GET /api/sessions/course-sessions/?teacher=2
GET /api/sessions/course-sessions/?course=3
```

#### Inscriptions d'une session
```http
GET /api/sessions/course-sessions/{id}/enrollments/
Authorization: Bearer {token}
```

#### Lister les inscriptions
```http
GET /api/sessions/enrollments/
Authorization: Bearer {token}

# Filtres
GET /api/sessions/enrollments/?student=5
GET /api/sessions/enrollments/?session=10
GET /api/sessions/enrollments/?status=ENROLLED
```

#### Abandonner une inscription
```http
POST /api/sessions/enrollments/{id}/drop/
Authorization: Bearer {token}
```

### 5. Notes (`/api/grades/`)

#### Lister les notes
```http
GET /api/grades/grades/
Authorization: Bearer {token}

# Filtres
GET /api/grades/grades/?student=5
GET /api/grades/grades/?enrollment=20
GET /api/grades/grades/?session=10
```

#### Créer une note
```http
POST /api/grades/grades/
Authorization: Bearer {token}
Content-Type: application/json

{
  "enrollment": 20,
  "evaluation_name": "Examen Final",
  "grade": 85.5,
  "weight": 40.0,
  "evaluation_date": "2024-12-15",
  "comments": "Excellent travail"
}
```

#### Statistiques des notes
```http
GET /api/grades/grades/statistics/
Authorization: Bearer {token}
```

#### Résumés de notes
```http
GET /api/grades/summaries/
Authorization: Bearer {token}

# Étudiants en échec
GET /api/grades/summaries/failing_students/
Authorization: Bearer {token}
```

#### Recalculer une note finale
```http
POST /api/grades/summaries/{id}/recalculate/
Authorization: Bearer {token}
```

### 6. Présences (`/api/attendance/`)

#### Enregistrements de présence
```http
GET /api/attendance/records/
Authorization: Bearer {token}

# Filtres
GET /api/attendance/records/?student=5
GET /api/attendance/records/?session=10
GET /api/attendance/records/?status=ABSENT
GET /api/attendance/records/?start_date=2024-09-01&end_date=2024-12-20
```

#### Créer un enregistrement
```http
POST /api/attendance/records/
Authorization: Bearer {token}
Content-Type: application/json

{
  "enrollment": 20,
  "date": "2024-11-15",
  "status": "PRESENT",
  "notes": ""
}
```

#### Créer plusieurs enregistrements
```http
POST /api/attendance/records/bulk_create/
Authorization: Bearer {token}
Content-Type: application/json

{
  "records": [
    {
      "enrollment": 20,
      "date": "2024-11-15",
      "status": "PRESENT"
    },
    {
      "enrollment": 21,
      "date": "2024-11-15",
      "status": "ABSENT"
    }
  ]
}
```

#### Résumés de présence
```http
GET /api/attendance/summaries/
Authorization: Bearer {token}

# Faible présence
GET /api/attendance/summaries/low_attendance/?threshold=70
```

#### Statistiques de présence
```http
GET /api/attendance/summaries/statistics/
Authorization: Bearer {token}
```

### 7. Machine Learning (`/api/ml/`)

#### Lister les modèles ML
```http
GET /api/ml/models/
Authorization: Bearer {token}

# Filtres
GET /api/ml/models/?model_type=DROPOUT_PREDICTION
GET /api/ml/models/?is_active=true
```

#### Activer un modèle
```http
POST /api/ml/models/{id}/activate/
Authorization: Bearer {token}
```

#### Entraîner un modèle
```http
POST /api/ml/models/{id}/train/
Authorization: Bearer {token}
Content-Type: application/json

{
  "parameters": {
    "n_estimators": 100,
    "max_depth": 10
  }
}
```

#### Jobs d'entraînement
```http
GET /api/ml/training-jobs/
Authorization: Bearer {token}

# Filtres
GET /api/ml/training-jobs/?model=1
GET /api/ml/training-jobs/?status=COMPLETED
```

### 8. Prédictions (`/api/predictions/`)

#### Lister les prédictions
```http
GET /api/predictions/predictions/
Authorization: Bearer {token}

# Filtres
GET /api/predictions/predictions/?student=5
GET /api/predictions/predictions/?risk_level=HIGH
GET /api/predictions/predictions/?is_at_risk=true
GET /api/predictions/predictions/?is_latest=true
```

#### Étudiants à risque
```http
GET /api/predictions/predictions/at_risk/
Authorization: Bearer {token}
```

#### Statistiques
```http
GET /api/predictions/predictions/statistics/
Authorization: Bearer {token}
```

**Réponse:**
```json
{
  "total_predictions": 50,
  "at_risk_count": 12,
  "risk_levels": {
    "critical": 3,
    "high": 9,
    "medium": 18,
    "low": 20
  },
  "average_risk_score": 45.5,
  "average_confidence": 87.2
}
```

#### Générer prédictions en masse
```http
POST /api/predictions/predictions/generate_bulk/
Authorization: Bearer {token}
Content-Type: application/json

{
  "ml_model_id": 1,
  "period_id": 1
}
```

#### Ajouter une intervention
```http
POST /api/predictions/predictions/{id}/add_intervention/
Authorization: Bearer {token}
Content-Type: application/json

{
  "intervention_type": "TUTORING",
  "priority": "HIGH",
  "title": "Tutorat en mathématiques",
  "description": "Séances de tutorat hebdomadaires",
  "estimated_impact": 30.0
}
```

#### Interventions recommandées
```http
GET /api/predictions/interventions/
Authorization: Bearer {token}

# Filtres
GET /api/predictions/interventions/?prediction=15
GET /api/predictions/interventions/?intervention_type=TUTORING
GET /api/predictions/interventions/?priority=URGENT
```

### 9. Alertes (`/api/alerts/`)

#### Lister les alertes
```http
GET /api/alerts/alerts/
Authorization: Bearer {token}

# Filtres
GET /api/alerts/alerts/?student=5
GET /api/alerts/alerts/?alert_type=DROPOUT_RISK
GET /api/alerts/alerts/?severity=CRITICAL
GET /api/alerts/alerts/?status=ACTIVE
GET /api/alerts/alerts/?assigned_to=2
```

#### Mes alertes
```http
GET /api/alerts/alerts/my_alerts/
Authorization: Bearer {token}
```

#### Alertes actives
```http
GET /api/alerts/alerts/active/
Authorization: Bearer {token}
```

#### Alertes critiques
```http
GET /api/alerts/alerts/critical/
Authorization: Bearer {token}
```

#### Créer une alerte
```http
POST /api/alerts/alerts/
Authorization: Bearer {token}
Content-Type: application/json

{
  "student": 5,
  "alert_type": "LOW_ATTENDANCE",
  "severity": "WARNING",
  "title": "Faible présence détectée",
  "message": "L'étudiant a un taux de présence de 65%.",
  "assigned_to": 2
}
```

#### Accuser réception
```http
POST /api/alerts/alerts/{id}/acknowledge/
Authorization: Bearer {token}
```

#### Résoudre une alerte
```http
POST /api/alerts/alerts/{id}/resolve/
Authorization: Bearer {token}
Content-Type: application/json

{
  "resolution_note": "Rencontre effectuée avec l'étudiant"
}
```

#### Rejeter une alerte
```http
POST /api/alerts/alerts/{id}/dismiss/
Authorization: Bearer {token}
Content-Type: application/json

{
  "dismiss_reason": "Fausse alerte"
}
```

#### Assigner une alerte
```http
POST /api/alerts/alerts/{id}/assign/
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": 3
}
```

#### Statistiques
```http
GET /api/alerts/alerts/statistics/
Authorization: Bearer {token}
```

#### Actions d'alerte
```http
GET /api/alerts/actions/
Authorization: Bearer {token}

# Créer une action
POST /api/alerts/actions/
Authorization: Bearer {token}
Content-Type: application/json

{
  "alert": 10,
  "action_type": "CONTACT_STUDENT",
  "description": "Courriel envoyé à l'étudiant",
  "scheduled_date": "2024-11-20T10:00:00Z"
}
```

## Exemples d'Utilisation

### Scénario 1: Obtenir la liste des étudiants à risque

```python
import requests

# 1. Authentification
token_response = requests.post(
    'http://localhost:8000/api/auth/token/',
    json={
        'email': 'admin@spas.ca',
        'password': 'admin123'
    }
)
token = token_response.json()['access']

# 2. Obtenir les prédictions à risque
headers = {'Authorization': f'Bearer {token}'}
predictions = requests.get(
    'http://localhost:8000/api/predictions/predictions/at_risk/',
    headers=headers
)

# 3. Afficher les résultats
for pred in predictions.json():
    print(f"{pred['student_name']}: {pred['risk_score']}% - {pred['risk_level']}")
```

### Scénario 2: Créer des alertes pour faible présence

```python
# Obtenir les résumés de présence faible
low_attendance = requests.get(
    'http://localhost:8000/api/attendance/summaries/low_attendance/?threshold=70',
    headers=headers
)

# Créer des alertes
for summary in low_attendance.json():
    alert = requests.post(
        'http://localhost:8000/api/alerts/alerts/',
        headers=headers,
        json={
            'student': summary['enrollment']['student']['id'],
            'alert_type': 'LOW_ATTENDANCE',
            'severity': 'WARNING',
            'title': f"Faible présence: {summary['student_name']}",
            'message': f"Taux de présence: {summary['attendance_rate']}%"
        }
    )
```

## Codes d'Erreur

| Code | Description |
|------|-------------|
| 200 | OK - Requête réussie |
| 201 | Created - Ressource créée |
| 202 | Accepted - Requête acceptée (traitement asynchrone) |
| 400 | Bad Request - Données invalides |
| 401 | Unauthorized - Token manquant ou invalide |
| 403 | Forbidden - Pas les permissions |
| 404 | Not Found - Ressource non trouvée |
| 500 | Internal Server Error - Erreur serveur |

## Pagination

Par défaut, les listes sont paginées avec 20 éléments par page.

```http
GET /api/students/?page=2&page_size=50
```

## Recherche et Filtres

```http
# Recherche textuelle
GET /api/students/?search=Alexandre

# Tri
GET /api/students/?ordering=last_name
GET /api/students/?ordering=-admission_date  # descendant

# Filtres multiples
GET /api/students/?status=ACTIVE&program=1&search=Tremblay
```

## Bonnes Pratiques

1. **Toujours inclure le token** dans les requêtes authentifiées
2. **Gérer le rafraîchissement** du token avant expiration
3. **Utiliser la pagination** pour les grandes listes
4. **Filtrer côté serveur** plutôt que côté client
5. **Gérer les erreurs** appropriément
6. **Respecter les limites de taux** (rate limiting)
