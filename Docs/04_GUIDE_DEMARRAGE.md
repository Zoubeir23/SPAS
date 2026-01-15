# 🚀 Guide de Démarrage - SPAS

Guide complet pour démarrer avec le projet SPAS.

**Version** : 2.1  
**Date** : 3 janvier 2026

---

## ⚡ Démarrage Rapide

### Frontend

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

### Backend

```bash
# 1. Aller dans le dossier backend
cd backend

# 2. Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer les données de test
python manage.py init_spas

# 6. Lancer le serveur
python manage.py runserver

# API disponible sur http://localhost:8000
```

---

## 👥 Comptes de Test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| **Admin** | admin@isi.edu | password123 |
| **Enseignant** | teacher@isi.edu | password123 |
| **Data Scientist** | ds@isi.edu | password123 |
| **Pédagogique** | pedagogical@isi.edu | password123 |

---

## 🔐 Contrôle d'Accès par Rôle

| Rôle | Accès Autorisés |
|------|-----------------|
| **admin** | Toutes les fonctionnalités + Utilisateurs + Paramètres |
| **teacher** | Dashboard, Étudiants, Notes, Absences, Sessions |
| **ds** | Dashboard Prédictif, ML, Prédictions, Analytics |
| **pedagogical** | Dashboards, Alertes, Interventions, Prédictions |

---

## 📁 Structure du Projet

```
SPAS/
├── frontend/src/
│   ├── pages/              # 18 pages React
│   │   ├── auth/           # Connexion, MotDePasseOublie
│   │   ├── dashboard/      # TableauDeBordGeneral, TableauDeBordPredictif
│   │   ├── students/       # ListeEtudiants, DetailEtudiant
│   │   ├── programs/       # ListeFilieres
│   │   ├── sessions/       # ListeSessions
│   │   ├── alerts/         # ListeAlertes
│   │   ├── predictions/    # DetailPrediction (+ SHAP)
│   │   ├── users/          # GestionUtilisateurs
│   │   ├── ml/             # GestionModeles, DetailModele (+ ROC)
│   │   ├── attendance/     # GestionAbsences
│   │   ├── grades/         # SaisieNotes
│   │   ├── settings/       # ParametresSysteme
│   │   └── analytics/      # AnalysesAvancees
│   │
│   ├── components/         # 26 composants UI
│   │   ├── common/         # Bouton, ChampSaisie, Carte, Badge...
│   │   ├── layout/         # MiseEnPagePrincipale, BarreLaterale, EnTete
│   │   ├── modals/         # ModaleEtudiant, ModaleUtilisateur...
│   │   └── charts/         # GraphiqueROC, GraphiqueSHAP, GraphiqueLignes...
│   │
│   ├── api/services/       # 12 services API (connectés)
│   ├── store/              # Zustand (état global)
│   └── routes/             # Configuration routes + protection par rôle
│
├── backend/
│   ├── apps/               # 10 applications Django
│   │   ├── authentication/ # JWT
│   │   ├── users/          # Utilisateurs (4 rôles)
│   │   ├── students/       # Étudiants
│   │   ├── programs/       # Programmes
│   │   ├── sessions/       # Sessions
│   │   ├── grades/         # Notes
│   │   ├── attendance/     # Présences
│   │   ├── ml/             # XGBoost + SHAP + SMOTE
│   │   ├── predictions/    # Prédictions
│   │   ├── alerts/         # Alertes + Interventions
│   │   └── core/           # Logs d'audit + Paramètres
│   └── config/             # Configuration Django
│
└── Docs/                   # Documentation

---

## 🎯 Routes Disponibles

### Routes Publiques
- `/auth/login` - Page de connexion
- `/auth/forgot-password` - Mot de passe oublié

### Routes Protégées (par rôle)

| Route | Admin | Teacher | DS | Pedagogical |
|-------|:-----:|:-------:|:--:|:-----------:|
| `/dashboard` | ✅ | ✅ | ✅ | ✅ |
| `/dashboard/predictive` | ✅ | ❌ | ✅ | ✅ |
| `/students` | ✅ | ✅ | ❌ | ✅ |
| `/students/:id` | ✅ | ✅ | ❌ | ✅ |
| `/programs` | ✅ | ✅ | ❌ | ✅ |
| `/sessions` | ✅ | ✅ | ❌ | ❌ |
| `/grades` | ✅ | ✅ | ❌ | ❌ |
| `/attendance` | ✅ | ✅ | ❌ | ❌ |
| `/predictions/:id` | ✅ | ❌ | ✅ | ✅ |
| `/alerts` | ✅ | ❌ | ❌ | ✅ |
| `/ml/models` | ✅ | ❌ | ✅ | ❌ |
| `/ml/models/:id` | ✅ | ❌ | ✅ | ❌ |
| `/analytics` | ✅ | ❌ | ✅ | ❌ |
| `/users` | ✅ | ❌ | ❌ | ❌ |
| `/settings` | ✅ | ❌ | ❌ | ❌ |

---

## 🛠️ Commandes Disponibles

### Frontend
```bash
npm run dev          # Lancer serveur dev (port 5173)
npm run build        # Build production
npm run preview      # Prévisualiser build
npm run test         # Lancer tests Vitest
npm run lint         # Vérifier code ESLint
```

### Backend
```bash
python manage.py runserver             # API (port 8000)
python manage.py migrate               # Appliquer migrations
python manage.py init_spas             # Créer données de test
python manage.py createsuperuser       # Admin Django
pytest                                 # Tests (28 passent)
```

---

## 🔧 Technologies

### Frontend
| Techno | Version | Usage |
|--------|---------|-------|
| React | 18.3.1 | Framework UI |
| TypeScript | 5.6.2 | Typage |
| Vite | 5.4.21 | Build tool |
| React Router | 7.1.1 | Routing |
| Zustand | 5.0.2 | État global |
| Axios | 1.7.9 | HTTP client |
| Tailwind CSS | 3.4.17 | Styling |
| Recharts | 2.15.0 | Graphiques (ROC, SHAP) |
| Lucide React | 0.469.0 | Icônes |

### Backend
| Techno | Version | Usage |
|--------|---------|-------|
| Django | 6.0 | Framework web |
| Django REST Framework | 3.15+ | API REST |
| PostgreSQL | 15+ | Base de données |
| Simple JWT | 5.3+ | Authentification |
| Celery | 5.3+ | Tâches async |
| Redis | 7+ | Broker Celery |

### Machine Learning
| Techno | Version | Usage |
|--------|---------|-------|
| XGBoost | 2.0+ | Algorithme principal |
| SHAP | 0.45+ | Explainability |
| imbalanced-learn | 0.12+ | SMOTE |
| scikit-learn | 1.3+ | Preprocessing |

---

## 📊 Données en Base (PostgreSQL)

| Entité | Nombre | Statut |
|--------|--------|--------|
| Étudiants | 66 | ✅ CRUD |
| Notes | 2602 | ✅ CRUD + CSV |
| Présences | 3857 | ✅ CRUD |
| Prédictions ML | 15 | ✅ Automatique |
| Alertes | 5 | ✅ Workflow |
| Programmes | 4 | ✅ CRUD |
| Sessions | 2 | ✅ CRUD |
| Modèles ML | 3 | ✅ Entraînement |
| Utilisateurs | 5 | ✅ 4 rôles |

---

## 📚 Documentation API

- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Admin Django** : http://localhost:8000/admin/

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
