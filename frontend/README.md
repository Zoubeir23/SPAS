# SPAS Frontend - Système Prédictif d'Alerte Scolaire

Application frontend React + TypeScript pour le système de prédiction d'abandon scolaire.

**Version** : 2.0  
**Statut** : Production Ready ✅

---

## 🚀 Technologies

| Technologie | Version | Description |
|-------------|---------|-------------|
| **React** | 18.3+ | Bibliothèque UI |
| **TypeScript** | 5.6+ | Typage statique |
| **Vite** | 5.4+ | Build tool ultra-rapide |
| **Tailwind CSS** | 3.4+ | Framework CSS utility-first |
| **React Router** | 7.1+ | Routing SPA |
| **Zustand** | 5.0+ | Gestion d'état minimaliste |
| **Recharts** | 2.15+ | Graphiques (ROC, SHAP, barres) |
| **React Hook Form + Zod** | - | Formulaires et validation |
| **Axios** | 1.7+ | Client HTTP |

---

## 📦 Installation

```bash
npm install
```

## 🛠️ Développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

## 🏗️ Build Production

```bash
npm run build
```

## 🧪 Tests

```bash
npm run test
```

## ✨ Formatage

```bash
npm run format
```

---

## 📁 Structure du projet

```
frontend/src/
├── api/                    # Services API connectés au backend Django
│   ├── services/           # Services par domaine (auth, students, ml, etc.)
│   ├── axiosConfig.ts      # Configuration Axios + intercepteurs JWT
│   └── endpoints.ts        # Constantes endpoints API
├── components/
│   ├── charts/             # Graphiques Recharts
│   │   ├── GraphiqueROC.tsx      # Courbe ROC interactive
│   │   ├── GraphiqueSHAP.tsx     # Visualisation facteurs SHAP
│   │   ├── GraphiqueLignes.tsx   # Line charts
│   │   ├── GraphiqueBarres.tsx   # Bar charts
│   │   └── GraphiqueCirculaire.tsx # Pie charts
│   ├── common/             # Composants réutilisables (Bouton, Carte, etc.)
│   ├── layout/             # Layout principal, sidebar, header
│   └── modals/             # Modales (étudiants, utilisateurs, ML)
├── pages/                  # 18 pages de l'application
│   ├── auth/               # Connexion, mot de passe oublié
│   ├── dashboard/          # Tableaux de bord (général + prédictif)
│   ├── students/           # Liste et détail étudiants
│   ├── ml/                 # Gestion modèles ML
│   ├── predictions/        # Détail prédictions avec SHAP
│   └── ...
├── routes/
│   ├── index.tsx           # Configuration routes avec restrictions par rôle
│   └── RouteProtegee.tsx   # Protection routes par authentification et rôle
├── store/                  # Store Zustand (authStore)
└── utils/                  # Utilitaires et constantes
```

---

## 🔐 Contrôle d'Accès par Rôle

Le frontend implémente un système de protection des routes par rôle utilisateur :

### Rôles disponibles
- `admin` - Accès complet
- `teacher` - Enseignant
- `ds` - Data Scientist
- `pedagogical` - Responsable pédagogique

### Exemple de protection de route

```tsx
// Dans routes/index.tsx
<Route
  path="/users"
  element={
    <RouteProtegee allowedRoles={['admin']}>
      <GestionUtilisateurs />
    </RouteProtegee>
  }
/>
```

### Restrictions appliquées

| Route | Rôles autorisés |
|-------|-----------------|
| `/dashboard` | admin, teacher, pedagogical |
| `/dashboard/predictive` | admin, ds, pedagogical |
| `/students` | admin, teacher, pedagogical |
| `/ml/models` | admin, ds |
| `/users` | admin |
| `/settings` | admin |

---

## 📊 Composants Graphiques

### Courbe ROC (`GraphiqueROC.tsx`)

Visualisation interactive des performances du modèle ML :
- Courbe ROC avec AUC
- Ligne diagonale (classificateur aléatoire)
- Point de seuil optimal
- Tooltip détaillé

### Graphique SHAP (`GraphiqueSHAP.tsx`)

Explication des prédictions via valeurs de Shapley :
- Barres horizontales colorées (rouge = augmente risque, vert = diminue)
- Contribution en pourcentage
- Valeurs observées
- Légende explicative SHAP

---

## 🔌 Services API

Tous les services sont connectés au backend Django :

| Service | Endpoint Backend | Description |
|---------|------------------|-------------|
| `authService` | `/api/auth/` | Login, logout, refresh JWT |
| `studentService` | `/api/students/` | CRUD étudiants |
| `mlService` | `/api/ml/` | Modèles ML, entraînement |
| `predictionService` | `/api/predictions/` | Prédictions avec SHAP |
| `alertService` | `/api/alerts/` | Alertes et interventions |
| `gradeService` | `/api/grades/` | Notes et moyennes |
| `attendanceService` | `/api/attendance/` | Présences |

---

## 👤 Auteur

**Zoubeir IBRAHIMA AMED**  
Projet SPAS - Mémoire de fin d'études

