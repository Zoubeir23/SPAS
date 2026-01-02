# Mapping des Dépendances Backend - SPAS Frontend

Ce document liste tous les endpoints API nécessaires pour que le frontend fonctionne avec le backend réel.

## 📋 Table des Matières

1. [Authentification](#authentification)
2. [Utilisateurs](#utilisateurs)
3. [Étudiants](#étudiants)
4. [Programmes](#programmes)
5. [Sessions](#sessions)
6. [Notes](#notes)
7. [Présences](#présences)
8. [Machine Learning](#machine-learning)
9. [Prédictions](#prédictions)
10. [Alertes](#alertes)
11. [Export (Optionnel)](#export-optionnel)

---

## 🔐 Authentification

### Service Frontend
- **Fichier**: `frontend/src/api/services/authService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `POST` | `/api/auth/token/` | Connexion (obtenir JWT) | `{ email, password }` | `{ access, refresh, user }` |
| `POST` | `/api/auth/token/refresh/` | Rafraîchir le token | `{ refresh }` | `{ access }` |
| `POST` | `/api/auth/token/verify/` | Vérifier le token | `{ token }` | `{ valid: boolean }` |
| `POST` | `/api/auth/forgot-password/` | Mot de passe oublié | `{ email }` | `{ message }` |
| `POST` | `/api/auth/reset-password/` | Réinitialiser mot de passe | `{ token, password }` | `{ message }` |
| `POST` | `/api/auth/logout/` | Déconnexion | `{ refresh }` | `{ message }` |

### Format User Object
```typescript
{
  id: string
  email: string
  firstName?: string
  lastName?: string
  role: 'admin' | 'teacher' | 'ds' | 'pedagogical'
}
```

---

## 👥 Utilisateurs

### Service Frontend
- **Fichier**: `frontend/src/pages/users/GestionUtilisateurs.tsx`
- **État actuel**: Données mockées dans le composant

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/users/` | Liste des utilisateurs | Query: `?role=admin&search=...` | `{ results: User[], count }` |
| `GET` | `/api/users/{id}/` | Détails utilisateur | - | `User` |
| `POST` | `/api/users/` | Créer utilisateur | `{ email, firstName, lastName, role, password }` | `User` |
| `PUT` | `/api/users/{id}/` | Modifier utilisateur | `{ firstName, lastName, role }` | `User` |
| `DELETE` | `/api/users/{id}/` | Supprimer utilisateur | - | `{ message }` |
| `GET` | `/api/users/me/` | Profil utilisateur actuel | - | `User` |
| `PUT` | `/api/users/update_profile/` | Modifier profil | `{ firstName, lastName }` | `User` |
| `POST` | `/api/users/change_password/` | Changer mot de passe | `{ oldPassword, newPassword }` | `{ message }` |

---

## 🎓 Étudiants

### Service Frontend
- **Fichier**: `frontend/src/api/services/studentService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/students/` | Liste des étudiants | Query: `?status=active&program=1&search=...` | `{ results: Student[], count }` |
| `GET` | `/api/students/{id}/` | Détails étudiant | - | `Student` |
| `POST` | `/api/students/` | Créer étudiant | `{ matricule, firstName, lastName, email, phone, dateOfBirth, programId, sessionId }` | `Student` |
| `PUT` | `/api/students/{id}/` | Modifier étudiant | `{ firstName, lastName, email, phone, ... }` | `Student` |
| `DELETE` | `/api/students/{id}/` | Supprimer étudiant | - | `{ message }` |
| `GET` | `/api/students/at_risk/` | Étudiants à risque | Query: `?level=high` | `Student[]` |

### Format Student Object
```typescript
{
  id: string
  matricule: string
  firstName: string
  lastName: string
  email: string
  phone?: string
  dateOfBirth?: string
  programId: string
  programName: string
  sessionId: string
  sessionName: string
  status: 'active' | 'inactive' | 'graduated'
  riskLevel?: 'low' | 'medium' | 'high' | 'critical'
  riskScore?: number
  photo?: string
}
```

---

## 📚 Programmes

### Service Frontend
- **Fichier**: `frontend/src/api/services/programService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/programs/programs/` | Liste des programmes | Query: `?active=true` | `Program[]` |
| `GET` | `/api/programs/programs/{id}/` | Détails programme | - | `Program` |
| `GET` | `/api/programs/courses/` | Liste des cours | Query: `?program=1` | `Course[]` |
| `GET` | `/api/programs/courses/{id}/` | Détails cours | - | `Course` |

---

## 📅 Sessions

### Service Frontend
- **Fichier**: `frontend/src/api/services/sessionService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/sessions/periods/` | Périodes académiques | Query: `?year=2024` | `Period[]` |
| `GET` | `/api/sessions/course-sessions/` | Sessions de cours | Query: `?period=1&course=1` | `CourseSession[]` |
| `GET` | `/api/sessions/enrollments/` | Inscriptions | Query: `?student=1&session=1` | `Enrollment[]` |
| `POST` | `/api/sessions/enrollments/` | Créer inscription | `{ studentId, sessionId }` | `Enrollment` |

---

## 📊 Notes

### Service Frontend
- **Fichier**: `frontend/src/api/services/gradeService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/grades/grades/` | Liste des notes | Query: `?student=1&course=1` | `Grade[]` |
| `GET` | `/api/grades/grades/{id}/` | Détails note | - | `Grade` |
| `POST` | `/api/grades/grades/` | Créer/modifier note | `{ studentId, courseId, value, type }` | `Grade` |
| `GET` | `/api/grades/summaries/` | Résumés de notes | Query: `?student=1` | `GradeSummary` |
| `GET` | `/api/grades/summaries/failing_students/` | Étudiants en échec | Query: `?threshold=10` | `Student[]` |

---

## ✅ Présences

### Service Frontend
- **Fichier**: `frontend/src/api/services/attendanceService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/attendance/records/` | Enregistrements de présence | Query: `?student=1&session=1` | `AttendanceRecord[]` |
| `POST` | `/api/attendance/records/` | Créer présence | `{ studentId, sessionId, date, status }` | `AttendanceRecord` |
| `POST` | `/api/attendance/records/bulk_create/` | Créer plusieurs présences | `{ records: [...] }` | `AttendanceRecord[]` |
| `GET` | `/api/attendance/summaries/low_attendance/` | Faible présence | Query: `?threshold=75` | `Student[]` |

---

## 🤖 Machine Learning

### Service Frontend
- **Fichier**: `frontend/src/api/services/mlService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/ml/models/` | Liste des modèles | - | `MLModel[]` |
| `GET` | `/api/ml/models/{id}/` | Détails modèle | - | `MLModel` |
| `POST` | `/api/ml/models/{id}/train/` | Lancer entraînement | `{ parameters }` | `{ jobId, status }` |
| `POST` | `/api/ml/models/{id}/activate/` | Activer modèle | - | `MLModel` |
| `GET` | `/api/ml/models/{id}/metrics/` | Métriques modèle | - | `{ accuracy, precision, recall, f1Score, ... }` |
| `GET` | `/api/ml/training-jobs/` | Jobs d'entraînement | Query: `?status=running` | `TrainingJob[]` |
| `GET` | `/api/ml/training-jobs/{id}/` | Détails job | - | `TrainingJob` |

### Format MLModel Object
```typescript
{
  id: string
  name: string
  version: string
  status: 'active' | 'inactive' | 'training'
  accuracy: number
  precision: number
  recall: number
  f1Score: number
  trainedAt: string
  trainingDataSize: number
}
```

---

## 🔮 Prédictions

### Service Frontend
- **Fichier**: `frontend/src/api/services/predictionService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/predictions/predictions/` | Liste des prédictions | Query: `?student=1&level=high` | `Prediction[]` |
| `GET` | `/api/predictions/predictions/{id}/` | Détails prédiction | - | `Prediction` |
| `POST` | `/api/predictions/predictions/generate_bulk/` | Générer prédictions | `{ studentIds?: [] }` | `{ jobId, count }` |
| `GET` | `/api/predictions/predictions/at_risk/` | Prédictions à risque | Query: `?level=critical` | `Prediction[]` |
| `GET` | `/api/predictions/predictions/statistics/` | Statistiques | Query: `?period=2024` | `{ total, byLevel, trends }` |
| `GET` | `/api/predictions/interventions/` | Interventions recommandées | Query: `?student=1` | `RecommendedIntervention[]` |

### Format Prediction Object
```typescript
{
  id: string
  studentId: string
  studentName: string
  riskScore: number // 0-100
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  confidence: number // 0-1
  factors: string[]
  generatedAt: string
}
```

---

## 🚨 Alertes

### Service Frontend
- **Fichier**: `frontend/src/api/services/alertService.ts`
- **État actuel**: Mock implémenté

### Endpoints Requis

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `GET` | `/api/alerts/alerts/` | Liste des alertes | Query: `?status=open&level=critical` | `Alert[]` |
| `GET` | `/api/alerts/alerts/{id}/` | Détails alerte | - | `Alert` |
| `POST` | `/api/alerts/alerts/{id}/acknowledge/` | Accuser réception | - | `Alert` |
| `POST` | `/api/alerts/alerts/{id}/resolve/` | Résoudre alerte | `{ resolution: string }` | `Alert` |
| `GET` | `/api/alerts/alerts/my_alerts/` | Mes alertes | - | `Alert[]` |
| `GET` | `/api/alerts/alerts/critical/` | Alertes critiques | - | `Alert[]` |

### Format Alert Object
```typescript
{
  id: string
  type: string
  level: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'acknowledged' | 'resolved'
  message: string
  studentId: string
  studentName: string
  programName: string
  createdAt: string
  assignedTo?: string
}
```

---

## 📤 Export (Optionnel)

### Service Frontend
- **Fichier**: `frontend/src/utils/exportService.ts`
- **État actuel**: Export côté client implémenté (PDF/Excel)

### Endpoints Optionnels

Ces endpoints sont **optionnels** car l'export fonctionne déjà côté client. Ils peuvent être ajoutés pour :
- Générer des rapports complexes côté serveur
- Traiter de grandes quantités de données
- Personnaliser les formats d'export

| Méthode | Endpoint | Description | Format Requête | Format Réponse |
|---------|----------|-------------|----------------|----------------|
| `POST` | `/api/export/pdf` | Générer PDF côté serveur | `{ type, filters, template }` | `{ fileUrl, expiresAt }` |
| `POST` | `/api/export/excel` | Générer Excel côté serveur | `{ type, filters }` | `{ fileUrl, expiresAt }` |

---

## 🔄 Migration depuis Mock vers Backend Réel

### Étapes de Migration

1. **Configurer l'URL de base du backend**
   - Modifier `frontend/src/api/axiosConfig.ts`
   - Définir `VITE_API_BASE_URL` dans `.env`

2. **Remplacer les services mockés**
   - Pour chaque service dans `frontend/src/api/services/`:
     - Remplacer les `setTimeout()` par des appels `axios`
     - Utiliser les endpoints listés ci-dessus
     - Gérer les erreurs HTTP correctement

3. **Gérer l'authentification JWT**
   - Intercepteurs axios pour ajouter le token
   - Refresh automatique du token
   - Gestion des erreurs 401/403

4. **Tester chaque fonctionnalité**
   - Authentification
   - CRUD pour chaque entité
   - Filtres et recherche
   - Pagination

### Exemple de Migration

**Avant (Mock)**:
```typescript
async getAll(): Promise<Student[]> {
  await new Promise((resolve) => setTimeout(resolve, 500))
  return [...mockStudents]
}
```

**Après (Backend)**:
```typescript
async getAll(filters?: { status?: string; program?: string }): Promise<Student[]> {
  const response = await axios.get('/api/students/', { params: filters })
  return response.data.results
}
```

---

## 📝 Notes Importantes

1. **Pagination**: La plupart des endpoints `GET` devraient supporter la pagination avec `?page=1&page_size=20`

2. **Filtres**: Les endpoints de liste devraient accepter des paramètres de filtrage via query strings

3. **Recherche**: Les endpoints de liste devraient supporter `?search=...` pour la recherche textuelle

4. **Permissions**: Tous les endpoints doivent vérifier les permissions selon le rôle de l'utilisateur

5. **Format de Date**: Utiliser le format ISO 8601 pour toutes les dates (`YYYY-MM-DDTHH:mm:ssZ`)

6. **Gestion d'Erreurs**: Tous les endpoints doivent retourner des erreurs au format:
   ```json
   {
     "error": "Message d'erreur",
     "code": "ERROR_CODE",
     "details": {}
   }
   ```

---

## ✅ Checklist d'Intégration

- [ ] Authentification JWT fonctionnelle
- [ ] Refresh token automatique
- [ ] CRUD Utilisateurs
- [ ] CRUD Étudiants
- [ ] Liste et filtres Programmes
- [ ] Gestion Sessions
- [ ] CRUD Notes
- [ ] CRUD Présences
- [ ] Liste et métriques Modèles ML
- [ ] Liste et génération Prédictions
- [ ] CRUD Alertes
- [ ] Export PDF/Excel (optionnel)

---

**Dernière mise à jour**: 2024-01-XX
**Version Frontend**: 0.1.0
**Version Backend Requise**: Compatible avec Django REST Framework

