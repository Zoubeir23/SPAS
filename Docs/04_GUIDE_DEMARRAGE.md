# 🚀 Guide de Démarrage - SPAS

Guide complet pour démarrer avec le projet SPAS.

---

## ⚡ Démarrage Rapide

### Frontend (Fonctionnel en mode démo)

```bash
# 1. Aller dans le dossier frontend
cd frontend

# 2. Installer les dépendances
npm install

# 3. Lancer le serveur de développement
npm run dev

# 4. Ouvrir dans le navigateur
# http://localhost:5173
```

### Login de Test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| **Admin** | sophie.martin@isi.edu | *N'importe quel* |
| **Teacher** | pierre.dupont@isi.edu | *N'importe quel* |
| **Data Scientist** | marie.sarr@isi.edu | *N'importe quel* |

**Note**: L'authentification est mockée, n'importe quel mot de passe fonctionne.

---

## 📁 Structure Frontend

```
frontend/src/
├── pages/              # 18 pages React
│   ├── auth/          # Login, ForgotPassword
│   ├── dashboard/     # GeneralDashboard, PredictiveDashboard
│   ├── students/      # StudentList, StudentDetail
│   ├── programs/      # ProgramList
│   ├── sessions/      # SessionList
│   ├── alerts/        # AlertList
│   ├── predictions/   # PredictionDetail
│   ├── users/         # UserManagement
│   ├── ml/            # ModelManagement, ModelDetails
│   ├── attendance/    # AttendanceManagement
│   ├── grades/        # GradeEntry
│   ├── settings/      # SystemSettings
│   └── analytics/     # AdvancedAnalytics
│
├── components/         # 22 composants UI
│   ├── common/        # Button, Input, Card, Badge, Alert...
│   ├── layout/        # MainLayout, Sidebar, Header
│   ├── modals/        # StudentModal, UserModal, TrainingModal...
│   └── charts/        # LineChart, BarChart, PieChart, GaugeChart
│
├── api/
│   ├── axiosConfig.ts
│   ├── endpoints.ts
│   └── services/      # 9 services API (mockés)
│
├── store/             # Zustand (état global)
├── hooks/             # Hooks personnalisés
├── routes/            # Configuration routes
└── utils/             # Utilitaires
```

---

## 🎯 Routes Disponibles

### Routes Publiques
- `/auth/login` - Page de connexion
- `/auth/forgot-password` - Mot de passe oublié

### Routes Protégées

#### Dashboards
- `/dashboard` - Dashboard général
- `/dashboard/predictive` - Dashboard prédictif ML

#### Gestion Académique
- `/students` - Liste des étudiants
- `/students/:id` - Détail étudiant
- `/programs` - Liste des filières
- `/sessions` - Liste des sessions
- `/grades` - Saisie des notes
- `/attendance` - Gestion des absences

#### Module IA
- `/predictions` - Prédictions ML
- `/alerts` - Alertes système
- `/ml/models` - Gestion modèles ML
- `/ml/models/:id` - Détails modèle

#### Administration
- `/users` - Gestion utilisateurs
- `/analytics` - Analytics avancées
- `/settings` - Paramètres système

---

## 🛠️ Commandes Disponibles

### Développement
```bash
npm run dev          # Lancer serveur dev (port 5173)
npm run build        # Build production
npm run preview      # Prévisualiser build
```

### Tests
```bash
npm run test         # Lancer tests (2 tests basiques)
npm run test:ui      # Tests avec interface
npm run coverage     # Rapport de couverture
```

### Qualité Code
```bash
npm run lint         # Vérifier code
npm run format       # Formater code (si configuré)
```

---

## 🔧 Technologies Utilisées

### Frontend
| Techno | Version | Usage |
|--------|---------|-------|
| React | 18.3.1 | Framework UI |
| TypeScript | 5.6.2 | Typage |
| Vite | 6.0.3 | Build tool |
| React Router | 7.1.1 | Routing |
| Zustand | 5.0.2 | État global |
| Axios | 1.7.9 | HTTP client |
| Tailwind CSS | 3.4.17 | Styling |
| Recharts | 2.15.0 | Graphiques |
| Lucide React | 0.469.0 | Icônes |

### Backend (À implémenter)
❌ Aucune technologie backend actuellement

**Recommandations**:
- **Option 1**: Node.js + Express + Prisma + PostgreSQL
- **Option 2**: Django + DRF + PostgreSQL
- **Option 3**: NestJS + TypeORM + PostgreSQL

---

## ⚠️ Limitations Actuelles

### 1. Données Mockées
Tous les services retournent des données simulées.

**Exemple**:
```typescript
// frontend/src/api/services/studentService.ts
export const getAll = async (): Promise<Student[]> => {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return mockStudents; // ❌ Données en dur
};
```

### 2. Pas de Persistance
Les modifications UI ne sont **PAS** sauvegardées.
- Créer un étudiant → Perdu au refresh
- Modifier une note → Perdu au refresh
- Supprimer un item → Perdu au refresh

### 3. Authentification Mockée
```typescript
// N'importe quel mot de passe fonctionne
if (email.includes('@isi.edu')) {
  return { success: true, token: 'fake-token' };
}
```

---

## 🚀 Prochaines Étapes pour Développement

### Phase 1: Backend (CRITIQUE)

#### Option A: Node.js + Express
```bash
# 1. Créer le dossier backend
mkdir backend && cd backend

# 2. Initialiser npm
npm init -y

# 3. Installer dépendances
npm install express cors dotenv
npm install prisma @prisma/client
npm install jsonwebtoken bcrypt
npm install -D typescript @types/node @types/express

# 4. Initialiser Prisma
npx prisma init

# 5. Créer schéma base de données
# Editer prisma/schema.prisma

# 6. Générer migrations
npx prisma migrate dev
```

#### Option B: Django
```bash
# 1. Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Installer Django
pip install django djangorestframework
pip install django-cors-headers
pip install psycopg2-binary

# 3. Créer projet
django-admin startproject config .

# 4. Créer apps
python manage.py startapp authentication
python manage.py startapp academic
python manage.py startapp prediction
```

### Phase 2: Connecter Frontend → Backend

1. **Mettre à jour endpoints**
```typescript
// frontend/src/api/endpoints.ts
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
```

2. **Remplacer services mockés**
```typescript
// Avant (mocké)
export const getAll = async (): Promise<Student[]> => {
  return mockStudents;
};

// Après (API réelle)
export const getAll = async (): Promise<Student[]> => {
  const response = await api.get<Student[]>('/students');
  return response.data;
};
```

### Phase 3: Base de Données

**Schéma PostgreSQL recommandé**:
```sql
CREATE TABLE students (
  id UUID PRIMARY KEY,
  matricule VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  program_id UUID REFERENCES programs(id),
  session_id UUID REFERENCES sessions(id),
  risk_score DECIMAL(5,2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- + 8 autres tables (programs, sessions, grades, etc.)
```

---

## 📝 Variables d'Environnement

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_ENV=development
```

### Backend (.env) - À créer
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/spas

# JWT
JWT_SECRET=your-super-secret-key-change-this
JWT_EXPIRES_IN=7d

# Server
PORT=8000
NODE_ENV=development

# CORS
CORS_ORIGIN=http://localhost:5173
```

---

## 🧪 Tests

### Tests Actuels
```bash
# 2 tests basiques uniquement
npm run test

# Fichiers testés:
# - components/common/__tests__/Button.test.tsx
# - components/common/__tests__/Input.test.tsx
```

### Tests à Ajouter
```bash
# Tests unitaires (composants)
# Tests d'intégration (services API)
# Tests E2E (Playwright/Cypress)
```

---

## 📚 Ressources

- [Documentation React](https://react.dev)
- [Documentation TypeScript](https://www.typescriptlang.org/docs)
- [Documentation Vite](https://vitejs.dev)
- [Documentation Tailwind CSS](https://tailwindcss.com/docs)
- [Documentation Zustand](https://docs.pmnd.rs/zustand)

---

## ❓ FAQ

### Q: Pourquoi les modifications ne sont pas sauvegardées ?
**R**: Les services API sont mockés. Ils retournent des données en dur. Il faut implémenter un vrai backend.

### Q: Comment ajouter un utilisateur de test ?
**R**: Les utilisateurs sont mockés dans `authService.ts`. Modifiez le tableau `mockUsers`.

### Q: L'application fonctionne-t-elle en production ?
**R**: Non. Elle est **uniquement** utilisable en démo. Un backend réel est **obligatoire** pour la production.

### Q: Peut-on déployer le frontend seul ?
**R**: Techniquement oui (Vercel, Netlify), mais inutile sans backend. L'app ne ferait que afficher des données mockées.

### Q: Quel backend choisir (Node.js vs Django) ?
**R**:
- **Node.js** : Si vous voulez full TypeScript (même langage que frontend)
- **Django** : Si vous préférez Python, plus robuste pour ML

---

**Date**: 2026-01-01
**Version**: 1.0
**Statut**: Frontend opérationnel en démo, Backend requis pour production
