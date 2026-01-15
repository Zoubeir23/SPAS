# 🔗 Mapping API - SPAS

Ce document liste tous les endpoints API du backend Django avec leur mapping vers les services frontend.

**Version** : 2.1  
**Date** : 3 janvier 2026  
**Statut** : ✅ 100% Connecté

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
11. [Interventions](#interventions)
12. [Logs d'Audit](#logs-daudit)

---

## 🔐 Authentification

### Service Frontend
- **Fichier** : `frontend/src/api/services/authService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/auth/login/` | Connexion (JWT) |
| `POST` | `/api/auth/logout/` | Déconnexion |
| `POST` | `/api/auth/token/refresh/` | Rafraîchir le token |
| `GET` | `/api/auth/me/` | Profil utilisateur actuel |

---

## 👥 Utilisateurs

### Service Frontend
- **Fichier** : `frontend/src/api/services/userService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/users/` | Liste des utilisateurs |
| `GET` | `/api/users/{id}/` | Détails utilisateur |
| `POST` | `/api/users/` | Créer utilisateur |
| `PUT` | `/api/users/{id}/` | Modifier utilisateur |
| `DELETE` | `/api/users/{id}/` | Supprimer utilisateur |
| `GET` | `/api/users/me/` | Profil utilisateur actuel |

---

## 🎓 Étudiants

### Service Frontend
- **Fichier** : `frontend/src/api/services/studentService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/students/` | Liste des étudiants |
| `GET` | `/api/students/{id}/` | Détails étudiant |
| `POST` | `/api/students/` | Créer étudiant |
| `PUT` | `/api/students/{id}/` | Modifier étudiant |
| `DELETE` | `/api/students/{id}/` | Supprimer étudiant |
| `GET` | `/api/students/at_risk/` | Étudiants à risque |
| `GET` | `/api/students/export_csv/` | Export CSV |
| `POST` | `/api/students/import_csv/` | Import CSV |

---

## 📚 Programmes

### Service Frontend
- **Fichier** : `frontend/src/api/services/programService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/programs/programs/` | Liste des programmes |
| `GET` | `/api/programs/programs/{id}/` | Détails programme |
| `GET` | `/api/programs/subjects/` | Liste des matières |
| `GET` | `/api/programs/subjects/{id}/` | Détails matière |

---

## 📅 Sessions

### Service Frontend
- **Fichier** : `frontend/src/api/services/sessionService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/sessions/sessions/` | Liste des sessions |
| `GET` | `/api/sessions/sessions/{id}/` | Détails session |
| `POST` | `/api/sessions/sessions/` | Créer session |
| `PUT` | `/api/sessions/sessions/{id}/` | Modifier session |

---

## 📊 Notes

### Service Frontend
- **Fichier** : `frontend/src/api/services/gradeService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/grades/grades/` | Liste des notes |
| `GET` | `/api/grades/grades/{id}/` | Détails note |
| `POST` | `/api/grades/grades/` | Créer note |
| `POST` | `/api/grades/grades/bulk-create/` | Création en masse |
| `PUT` | `/api/grades/grades/{id}/` | Modifier note |
| `GET` | `/api/grades/grades/export_csv/` | Export CSV |
| `POST` | `/api/grades/grades/import_csv/` | Import CSV |

---

## ✅ Présences

### Service Frontend
- **Fichier** : `frontend/src/api/services/attendanceService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/attendance/attendance/` | Liste des présences |
| `GET` | `/api/attendance/attendance/{id}/` | Détails présence |
| `POST` | `/api/attendance/attendance/` | Créer présence |
| `PUT` | `/api/attendance/attendance/{id}/` | Modifier présence |

---

## 🧠 Machine Learning

### Service Frontend
- **Fichier** : `frontend/src/api/services/mlService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/ml/models/` | Liste des modèles |
| `GET` | `/api/ml/models/{id}/` | Détails modèle + métriques |
| `POST` | `/api/ml/models/{id}/activate/` | Activer modèle |
| `GET` | `/api/ml/models/active/` | Modèle actif |
| `POST` | `/api/ml/training/train/` | Lancer entraînement |
| `GET` | `/api/ml/models/{id}/roc_curve/` | Courbe ROC (AUC + seuil) |

### Algorithmes ML
- **XGBoost** : Algorithme principal (Gradient Boosting)
- **SHAP TreeExplainer** : Explainability via valeurs de Shapley
- **SMOTE** : Rééquilibrage des classes minoritaires
- **RandomForest** : Fallback si XGBoost échoue

---

## 🔮 Prédictions

### Service Frontend
- **Fichier** : `frontend/src/api/services/predictionService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/predictions/predictions/` | Liste des prédictions |
| `GET` | `/api/predictions/predictions/{id}/` | Détails prédiction + SHAP |
| `POST` | `/api/predictions/predictions/{id}/generate/` | Générer prédiction |

### Format Prediction (avec SHAP)
```typescript
{
  id: string
  student: Student
  risk_score: number        // 0-100
  risk_level: 'low' | 'medium' | 'high'
  factors: ShapFactor[]     // Facteurs SHAP explicables
  created_at: string
}
```

---

## 🚨 Alertes

### Service Frontend
- **Fichier** : `frontend/src/api/services/alertService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/alerts/alerts/` | Liste des alertes |
| `GET` | `/api/alerts/alerts/{id}/` | Détails alerte |
| `POST` | `/api/alerts/alerts/{id}/acknowledge/` | Accuser réception |
| `POST` | `/api/alerts/alerts/{id}/resolve/` | Résoudre alerte |

### Workflow des Alertes
```
new → acknowledged → resolved
```

---

## 📋 Interventions

### Service Frontend
- **Fichier** : `frontend/src/api/services/interventionService.ts`
- **État** : ✅ Connecté au backend Django

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/alerts/interventions/` | Liste des interventions |
| `GET` | `/api/alerts/interventions/{id}/` | Détails intervention |
| `POST` | `/api/alerts/interventions/` | Créer intervention |
| `PUT` | `/api/alerts/interventions/{id}/` | Modifier intervention |

---

## 📜 Logs d'Audit

### Service Frontend
- **Fichier** : Disponible via API directe
- **État** : ✅ Disponible (admin seulement)

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/core/audit-logs/` | Liste des logs |
| `GET` | `/api/core/audit-logs/{id}/` | Détails log |
| `GET` | `/api/core/audit-logs/my_activity/` | Mes actions |
| `GET` | `/api/core/audit-logs/recent/` | Actions récentes |

---

## 📊 Résumé de l'Intégration

| Service Frontend | Endpoint Backend | Statut |
|-----------------|------------------|--------|
| authService | /api/auth/ | ✅ Connecté |
| userService | /api/users/ | ✅ Connecté |
| studentService | /api/students/ | ✅ Connecté |
| programService | /api/programs/ | ✅ Connecté |
| sessionService | /api/sessions/ | ✅ Connecté |
| gradeService | /api/grades/ | ✅ Connecté |
| attendanceService | /api/attendance/ | ✅ Connecté |
| mlService | /api/ml/ | ✅ Connecté |
| predictionService | /api/predictions/ | ✅ Connecté |
| alertService | /api/alerts/ | ✅ Connecté |
| interventionService | /api/alerts/interventions/ | ✅ Connecté |

**Total** : 12/12 services connectés (100%)

---

## 📚 Documentation

- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Admin Django** : http://localhost:8000/admin/

---

**Auteur** : Zoubeir IBRAHIMA AMED  
**Dernière mise à jour** : 3 janvier 2026  
**Version Backend** : Django 6.0 + DRF 3.15+

