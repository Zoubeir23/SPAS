# 🔌 Intégration Frontend/Backend - SPAS

## État de l'Intégration

**Date de mise à jour** : 2 janvier 2026  
**Phase** : Phase 1 - Connexion Frontend/Backend ✅ COMPLÉTÉE

## Fichiers Modifiés

### 1. Configuration des Endpoints (`src/api/endpoints.ts`)

Tous les endpoints API Django REST Framework sont maintenant configurés :

```typescript
API_ENDPOINTS = {
  AUTH: { ... },      // 13 endpoints d'authentification
  USERS: { ... },     // 6 endpoints utilisateurs
  STUDENTS: { ... },  // 6 endpoints étudiants
  PROGRAMS: { ... },  // 3 endpoints programmes
  SUBJECTS: { ... },  // 2 endpoints matières
  SESSIONS: { ... },  // 3 endpoints sessions
  GRADES: { ... },    // 5 endpoints notes
  ATTENDANCE: { ... }, // 3 endpoints présences
  ML: { ... },        // 5 endpoints modèles ML
  PREDICTIONS: { ... }, // 6 endpoints prédictions
  ALERTS: { ... },    // 8 endpoints alertes
}
```

### 2. Services API Connectés

| Service | Fichier | Méthodes |
|---------|---------|----------|
| Auth | `authService.ts` | login, logout, forgotPassword, resetPassword, changePassword, refreshToken, getCurrentUser, verifyToken, register |
| Students | `studentService.ts` | getAll, getById, create, update, delete, getAtRisk |
| Programs | `programService.ts` | getAll, getById, create, update, delete |
| Subjects | `programService.ts` | getAll, getById, create, update, delete |
| Sessions | `sessionService.ts` | getAll, getById, create, update, delete |
| Grades | `gradeService.ts` | getAll, getById, create, update, delete, getByStudent, bulkCreate, getStatistics |
| Attendance | `attendanceService.ts` | getAll, getById, create, update, delete, getByStudent |
| ML Models | `mlService.ts` | getAll, getById, trainModel, startTraining, activate, deactivate, delete, getActiveModel, getPerformance |
| Predictions | `predictionService.ts` | getAll, getById, getByStudentId, getHighRisk, getStatistics, getDistribution |
| Alerts | `alertService.ts` | getAll, getById, acknowledge, resolve, getUnread, getStatistics, getByType, getByStudent |
| Users | `userService.ts` | getAll, getById, create, update, delete, changePassword, getCurrentUser, activate, deactivate |

### 3. Améliorations Axios (`src/api/axiosConfig.ts`)

- ✅ Refresh token automatique (gestion des 401)
- ✅ Queue des requêtes pendant le refresh
- ✅ Redirection automatique vers login si refresh échoue
- ✅ Timeout augmenté à 15 secondes

### 4. Store Auth (`src/store/authStore.ts`)

- ✅ Ajout de la méthode `setToken()` pour le refresh

## Normalisation des Données

Tous les services normalisent automatiquement les données entre le format Django (snake_case) et le format TypeScript (camelCase) :

```typescript
// Exemple: normalizeStudent
{
  first_name: "Jean",     // Django
  firstName: "Jean",      // TypeScript (ajouté automatiquement)
  program_id: "1",        // Django
  programId: "1",         // TypeScript (ajouté automatiquement)
}
```

## Comment Tester

### 1. Démarrer le Backend

```bash
cd backend
# Activer l'environnement virtuel
.\myenv\Scripts\activate  # Windows
source myenv/bin/activate  # Linux/Mac

# Démarrer le serveur
python manage.py runserver
```

### 2. Démarrer le Frontend

```bash
cd frontend
npm run dev
```

### 3. Tester l'authentification

1. Aller sur `http://localhost:5173/auth/login`
2. Se connecter avec un utilisateur créé via `python manage.py init_spas`
3. Vérifier que le token est stocké dans localStorage (`auth-storage`)

## Endpoints Backend Correspondants

| Frontend Service | Backend App | URL Prefix |
|-----------------|-------------|------------|
| authService | apps/authentication | `/api/auth/` |
| userService | apps/users | `/api/users/` |
| studentService | apps/students | `/api/students/` |
| programService | apps/programs | `/api/programs/programs/` |
| subjectService | apps/programs | `/api/programs/subjects/` |
| sessionService | apps/sessions | `/api/sessions/sessions/` |
| gradeService | apps/grades | `/api/grades/grades/` |
| attendanceService | apps/attendance | `/api/attendance/attendance/` |
| mlService | apps/ml | `/api/ml/models/` |
| predictionService | apps/predictions | `/api/predictions/predictions/` |
| alertService | apps/alerts | `/api/alerts/alerts/` |

## Prochaines Étapes

- [ ] Corriger les erreurs TypeScript pré-existantes dans les composants
- [ ] Tester chaque service avec le backend réel
- [ ] Implémenter le vrai algorithme ML (actuellement placeholder)
- [ ] Ajouter des tests d'intégration E2E
