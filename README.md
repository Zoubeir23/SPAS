# SPAS - Système Prédictif d'Alerte Scolaire

Système de gestion académique avec prédictions ML pour identifier les étudiants à risque.

## 📊 État du Projet

- **Frontend** : ✅ 100% Implémenté (React + TypeScript + Vite)
- **Backend** : ❌ 0% (À implémenter - Django + PostgreSQL)
- **Base de Données** : ❌ 0% (À créer - PostgreSQL)
- **Tests** : ⚠️ 5% (Tests basiques uniquement)

### Score Global : ~50%

---

## 🚀 Démarrage Rapide

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend (À venir)
```bash
cd backend
# Configuration Django + PostgreSQL
```

---

## 📚 Documentation

### Documentation Principale
Consultez le dossier **[Docs/](Docs/)** pour la documentation complète :

- **[Docs/README.md](Docs/README.md)** - Index de la documentation
- **[Docs/01_RAPPORT_ETAT_PROJET.md](Docs/01_RAPPORT_ETAT_PROJET.md)** - État détaillé du projet
- **[Docs/02_ARCHITECTURE_COMPLETE.txt](Docs/02_ARCHITECTURE_COMPLETE.txt)** - Architecture complète
- **[Docs/03_TESTS_DASHBOARDS.md](Docs/03_TESTS_DASHBOARDS.md)** - Tests des dashboards
- **[Docs/04_GUIDE_DEMARRAGE.md](Docs/04_GUIDE_DEMARRAGE.md)** - Guide de démarrage

### Rapports Importants à la Racine
- **[RAPPORT_TESTS_FINAUX.md](RAPPORT_TESTS_FINAUX.md)** - Rapport de tests complet
- **[RAPPORT_CONFORMITE_UML.md](RAPPORT_CONFORMITE_UML.md)** - Vérification conformité UML

### Architecture
- **[Architecture/Architecture.txt](Architecture/Architecture.txt)** - Architecture mise à jour (Django + PostgreSQL)

---

## 🏗️ Structure du Projet

```
SPAS/
├── frontend/          ✅ React + TypeScript (100%)
├── backend/           ❌ Django + PostgreSQL (0% - À créer)
├── Docs/              ✅ Documentation organisée
├── Architecture/      ✅ Documentation architecture
└── uml/               ✅ Diagrammes UML
```

---

## 🎯 Fonctionnalités

### Frontend (Implémenté)
- ✅ 18 pages complètes
- ✅ 22 composants UI réutilisables
- ✅ Authentification (mockée)
- ✅ Dashboards (Général + Prédictif)
- ✅ Gestion étudiants, sessions, filières
- ✅ Module ML (UI)
- ✅ Analytics avancées

### Backend (À implémenter)
- ❌ API REST Django
- ❌ Base de données PostgreSQL
- ❌ Authentification JWT réelle
- ❌ Modèles ML réels
- ❌ Calculs prédictifs

---

## 👥 Utilisateurs Mockés (Pour Tests)

| Email | Rôle | Dashboard |
|-------|------|-----------|
| sophie.martin@isi.edu | Admin | `/dashboard` |
| pierre.dupont@isi.edu | Teacher | `/dashboard` |
| marie.sarr@isi.edu | Data Scientist | `/dashboard/predictive` |

**Mot de passe** : `password123` (ou n'importe quel mot de passe ≥ 8 caractères)

---

## 📦 Technologies

### Frontend
- React 18.3.1
- TypeScript 5.6.2
- Vite 6.0.3
- Tailwind CSS 3.4.17
- React Router DOM 7.1.1
- Zustand 5.0.2
- Recharts 2.15.0

### Backend (Choisi)
- Django 5.x
- Django REST Framework
- PostgreSQL 15+
- djangorestframework-simplejwt
- Celery + Redis (recommandé)

---

## ⚠️ Limitations Actuelles

1. **Données Mockées** : Tous les services retournent des données simulées
2. **Backend Absent** : Aucune API réelle, aucune base de données
3. **Tests Basiques** : Couverture < 10%
4. **Pas de Persistance** : Modifications UI uniquement

---

## 🎯 Prochaines Étapes

1. **Phase 1** : Implémenter backend Django + PostgreSQL
2. **Phase 2** : Remplacer services mockés par vraies API
3. **Phase 3** : Implémenter module ML réel
4. **Phase 4** : Tests complets (>80% couverture)
5. **Phase 5** : Déploiement

Consultez **[Architecture/Architecture.txt](Architecture/Architecture.txt)** pour le plan détaillé.

---

## 📧 Contact

Pour toute question, consultez la documentation dans le dossier **[Docs/](Docs/)**.

---

**Version** : 1.0  
**Date** : 2026-01-16  
**Stack Backend** : Django + PostgreSQL


