# SPAS - Système Prédictif d'Alerte Scolaire

Système de gestion académique avec prédictions ML pour identifier les étudiants à risque d'abandon scolaire.

## 📊 État du Projet

- **Frontend** : ✅ 100% Implémenté (React + TypeScript + Vite)
- **Backend** : ✅ 100% Implémenté (Django 6.0 + PostgreSQL)
- **Machine Learning** : ✅ 100% (XGBoost + SHAP + SMOTE)
- **Tests** : ✅ 28 tests d'intégration passent

### Score Global : 100% - PROJET TERMINÉ ✅

---

## 🚀 Démarrage Rapide

### Frontend
```bash
cd frontend
npm install
npm run dev
# Accessible sur http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py init_spas  # Données de test
python manage.py runserver
# API sur http://localhost:8000
```

---

## 🧠 Machine Learning

### Algorithmes Implémentés

| Algorithme | Description |
|------------|-------------|
| **XGBoost** | Algorithme principal de classification (Gradient Boosting optimisé) |
| **SHAP** | Explainability - Valeurs de Shapley pour interpréter les prédictions |
| **SMOTE** | Rééquilibrage des classes minoritaires (étudiants à risque) |
| **Courbe ROC** | Visualisation interactive des performances du modèle |

### Fonctionnalités ML

- Prédiction du risque d'abandon (score 0-100%)
- Facteurs de risque expliqués via SHAP
- Entraînement automatique via Celery
- Courbe ROC interactive avec seuil optimal
- Support multi-algorithmes (XGBoost, RandomForest, GradientBoosting)

---

## 🔐 Sécurité et Contrôle d'Accès

### Rôles Utilisateurs

| Rôle | Accès |
|------|-------|
| **Admin** | Toutes les fonctionnalités + Paramètres + Utilisateurs |
| **Teacher** | Étudiants, Notes, Absences, Dashboard général |
| **Data Scientist** | ML, Prédictions, Analytics, Dashboard prédictif |
| **Pedagogical** | Dashboards, Alertes, Interventions, Analytics |

### Protection des Routes

- Routes frontend protégées par rôle (`allowedRoles`)
- Navigation dynamique filtrée selon le rôle connecté
- Authentification JWT avec refresh tokens

---

## 📚 Documentation

### Documentation Principale
- **[Docs/README.md](Docs/README.md)** - Index de la documentation
- **[backend/API_GUIDE.md](backend/API_GUIDE.md)** - Documentation API complète
- **[backend/STRUCTURE_BACKEND.md](backend/STRUCTURE_BACKEND.md)** - Architecture backend
- **[Architecture/Architecture.txt](Architecture/Architecture.txt)** - Architecture complète

### APIs Disponibles
- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Admin Django** : http://localhost:8000/admin/

---

## 🏗️ Structure du Projet

```
SPAS/
├── frontend/          ✅ React 18 + TypeScript + Vite
│   ├── src/pages/     18 pages complètes
│   ├── src/components/ 24+ composants (dont graphiques ROC, SHAP)
│   └── src/api/       Services connectés à l'API Django
├── backend/           ✅ Django 6.0 + DRF + PostgreSQL
│   ├── apps/          10 applications Django
│   ├── config/        Configuration Django
│   └── tests/         Tests pytest
├── Docs/              ✅ Documentation
└── Architecture/      ✅ Diagrammes et architecture
```

---

## 🎯 Fonctionnalités

### Frontend
- ✅ 18 pages complètes
- ✅ 24+ composants UI réutilisables
- ✅ Authentification JWT
- ✅ Dashboards (Général + Prédictif)
- ✅ Graphique ROC interactif
- ✅ Visualisation SHAP des facteurs de risque
- ✅ Contrôle d'accès par rôle
- ✅ Navigation dynamique

### Backend
- ✅ API REST complète (50+ endpoints)
- ✅ 10 applications Django modulaires
- ✅ Authentification JWT (Simple JWT)
- ✅ XGBoost + SHAP + SMOTE
- ✅ Logs d'audit avec statistiques
- ✅ Tâches asynchrones Celery
- ✅ Documentation OpenAPI 3.0

---

## 👥 Comptes de Test

| Email | Rôle | Mot de passe |
|-------|------|--------------|
| admin@isi.edu | Admin | password123 |
| teacher@isi.edu | Enseignant | password123 |
| ds@isi.edu | Data Scientist | password123 |
| pedagogical@isi.edu | Pédagogique | password123 |

---

## 📦 Technologies

### Frontend
- React 18.3.1
- TypeScript 5.6.2
- Vite 5.4.21
- Tailwind CSS 3.4.17
- React Router DOM 7.1.1
- Zustand 5.0.2
- Recharts 2.15.0 (Courbes ROC, graphiques SHAP)

### Backend
- Django 6.0
- Django REST Framework 3.15+
- PostgreSQL 15+
- Simple JWT (Authentification)
- Celery + Redis (Tâches asynchrones)
- XGBoost 2.0+ (Machine Learning)
- SHAP 0.45+ (Explainability)
- imbalanced-learn 0.12+ (SMOTE)

---

## 📧 Contact

**Auteur** : Zoubeir IBRAHIMA AMED  
**Projet** : Mémoire de fin d'études - Système Prédictif d'Alerte Scolaire  
**Repository** : github.com/Zoubeir23/SPAS

---

**Version** : 2.0  
**Date** : 3 janvier 2026  
**Statut** : Production Ready ✅


