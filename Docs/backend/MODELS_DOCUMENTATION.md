# Documentation des Modèles Django - SPAS

Ce document présente tous les modèles Django créés pour le projet SPAS (Student Performance Analytics System), organisés par application.

## Table des Matières

1. [students - Étudiants](#1-app-students)
2. [programs - Programmes et Matières](#2-app-programs)
3. [sessions - Sessions Académiques](#3-app-sessions)
4. [grades - Notes](#4-app-grades)
5. [attendance - Présences](#5-app-attendance)
6. [users - Utilisateurs](#6-app-users)
7. [ml - Modèles Machine Learning](#7-app-ml)
8. [predictions - Prédictions ML](#8-app-predictions)
9. [alerts - Alertes](#9-app-alerts)

---

## 1. App: students

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\students\models.py`

### Modèle: Student

Représente un étudiant dans le système.

**Champs principaux**:
- `matricule` (CharField, unique) - Numéro d'identification unique
- `first_name` (CharField) - Prénom
- `last_name` (CharField) - Nom de famille
- `email` (EmailField, unique) - Email de l'étudiant
- `phone` (CharField, nullable) - Téléphone
- `date_of_birth` (DateField) - Date de naissance
- `program` (ForeignKey → Program) - Programme d'études
- `session` (ForeignKey → Session) - Session académique
- `status` (CharField, choices) - Statut: active/inactive/graduated
- `risk_level` (CharField, choices, nullable) - Niveau de risque: low/medium/high
- `risk_score` (IntegerField, 0-100, nullable) - Score de risque

**Méthodes**:
- `get_full_name()` - Retourne le nom complet
- `update_risk_assessment(risk_score, risk_level)` - Met à jour l'évaluation de risque

**Propriétés**:
- `program_name` - Nom du programme
- `session_name` - Nom de la session

---

## 2. App: programs

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\programs\models.py`

### Modèle: Program

Représente une filière/programme d'études.

**Champs principaux**:
- `name` (CharField) - Nom du programme
- `code` (CharField, unique) - Code unique du programme
- `description` (TextField, nullable) - Description
- `duration` (IntegerField) - Durée en années
- `status` (CharField, choices) - Statut: active/inactive

**Méthodes**:
- `get_active_students()` - Retourne les étudiants actifs

**Propriétés**:
- `student_count` - Nombre d'étudiants actifs dans le programme

### Modèle: Subject

Représente une matière/cours.

**Champs principaux**:
- `name` (CharField) - Nom de la matière
- `code` (CharField, unique) - Code unique de la matière
- `description` (TextField, nullable) - Description
- `programs` (ManyToManyField → Program) - Programmes incluant cette matière

---

## 3. App: sessions

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\sessions\models.py`

### Modèle: Session

Représente une session académique (année scolaire/semestre).

**Champs principaux**:
- `name` (CharField) - Nom de la session
- `year` (CharField) - Année académique (ex: "2023-2024")
- `start_date` (DateField) - Date de début
- `end_date` (DateField) - Date de fin
- `status` (CharField, choices) - Statut: active/inactive/completed

**Méthodes**:
- `is_current()` - Vérifie si la session est en cours
- `get_active_students()` - Retourne les étudiants actifs

**Propriétés**:
- `student_count` - Nombre d'étudiants actifs dans la session

**Contraintes**:
- `unique_together`: ['name', 'year']

---

## 4. App: grades

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\grades\models.py`

### Modèle: Grade

Représente une note obtenue par un étudiant.

**Champs principaux**:
- `student` (ForeignKey → Student) - Étudiant
- `subject` (ForeignKey → Subject) - Matière
- `session` (ForeignKey → Session) - Session académique
- `value` (DecimalField) - Note obtenue
- `max_value` (DecimalField) - Note maximale possible
- `type` (CharField, choices) - Type: exam/assignment/project/participation
- `date` (DateField) - Date de l'évaluation

**Méthodes**:
- `is_passing(passing_threshold=60)` - Vérifie si la note est suffisante

**Propriétés**:
- `student_name` - Nom de l'étudiant
- `subject_name` - Nom de la matière
- `session_name` - Nom de la session
- `percentage` - Note en pourcentage

---

## 5. App: attendance

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\attendance\models.py`

### Modèle: Attendance

Représente un enregistrement de présence.

**Champs principaux**:
- `student` (ForeignKey → Student) - Étudiant
- `subject` (ForeignKey → Subject) - Matière
- `date` (DateField) - Date de la présence
- `status` (CharField, choices) - Statut: present/absent/late/excused
- `justification` (TextField, nullable) - Justification d'absence

**Méthodes**:
- `is_present()` - Vérifie si l'étudiant était présent
- `is_justified()` - Vérifie si l'absence est justifiée

**Propriétés**:
- `student_name` - Nom de l'étudiant
- `subject_name` - Nom de la matière

**Contraintes**:
- `unique_together`: ['student', 'subject', 'date']

---

## 6. App: users

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\users\models.py`

### Modèle: User

Modèle d'utilisateur personnalisé (hérite de AbstractUser).

**Champs principaux**:
- `email` (EmailField, unique) - Email (utilisé comme username)
- `first_name` (CharField) - Prénom
- `last_name` (CharField) - Nom
- `role` (CharField, choices) - Rôle: admin/teacher/ds/pedagogical
- `phone` (CharField, nullable) - Téléphone
- `is_active` (BooleanField) - Compte actif

**Méthodes**:
- `get_full_name()` - Retourne le nom complet
- `is_admin()` - Vérifie si admin
- `is_teacher()` - Vérifie si enseignant
- `is_ds()` - Vérifie si directeur des études
- `is_pedagogical()` - Vérifie si conseiller pédagogique
- `has_elevated_permissions()` - Vérifie si l'utilisateur a des permissions élevées

**Permissions personnalisées**:
- `can_view_analytics` - Voir le tableau de bord analytique
- `can_manage_students` - Gérer les étudiants
- `can_manage_programs` - Gérer les programmes
- `can_manage_grades` - Gérer les notes
- `can_manage_attendance` - Gérer les présences
- `can_run_ml_predictions` - Exécuter les prédictions ML
- `can_view_predictions` - Voir les prédictions ML
- `can_manage_alerts` - Gérer les alertes

**Manager personnalisé**: UserManager

---

## 7. App: ml

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\ml\models.py`

### Modèle: MLModel

Représente un modèle de machine learning entraîné.

**Champs principaux**:
- `name` (CharField) - Nom du modèle
- `version` (CharField) - Version du modèle
- `status` (CharField, choices) - Statut: active/inactive/training
- `accuracy` (DecimalField, 0-100) - Précision du modèle
- `precision` (DecimalField, 0-100) - Précision
- `recall` (DecimalField, 0-100) - Rappel
- `f1_score` (DecimalField, 0-100) - Score F1
- `trained_at` (DateTimeField) - Date d'entraînement
- `training_data_size` (IntegerField) - Taille des données d'entraînement

**Méthodes**:
- `activate()` - Active ce modèle et désactive les autres
- `is_active()` - Vérifie si le modèle est actif

**Propriétés**:
- `average_score` - Score moyen de toutes les métriques

**Contraintes**:
- `unique_together`: ['name', 'version']

---

## 8. App: predictions

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\predictions\models.py`

### Modèle: Prediction

Représente une prédiction ML pour un étudiant.

**Champs principaux**:
- `student` (ForeignKey → Student) - Étudiant
- `model_version` (ForeignKey → MLModel) - Version du modèle ML
- `risk_score` (IntegerField, 0-100) - Score de risque
- `risk_level` (CharField, choices) - Niveau: low/medium/high/critical
- `predicted_success_rate` (IntegerField, 0-100) - Taux de réussite prédit
- `factors` (JSONField) - Facteurs contributifs au format: [{"name": "attendance", "impact": 0.45}, ...]
- `created_at` (DateTimeField) - Date de création

**Méthodes**:
- `save()` - Calcule automatiquement risk_level et met à jour l'étudiant
- `get_top_factors(limit=5)` - Retourne les N principaux facteurs

**Propriétés**:
- `student_name` - Nom de l'étudiant
- `model_version_name` - Nom et version du modèle

**Logique de risk_level**:
- score >= 75: CRITICAL
- score >= 50: HIGH
- score >= 25: MEDIUM
- score < 25: LOW

---

## 9. App: alerts

**Fichier**: `C:\Users\Public\Libraries\one\SPAS\backend\apps\alerts\models.py`

### Modèle: Alert

Représente une alerte automatique concernant un étudiant.

**Champs principaux**:
- `student` (ForeignKey → Student) - Étudiant concerné
- `type` (CharField, choices) - Type: performance/attendance/risk/prediction
- `level` (CharField, choices) - Niveau: low/medium/high/critical
- `message` (TextField) - Message de l'alerte
- `status` (CharField, choices) - Statut: new/acknowledged/resolved
- `created_at` (DateTimeField) - Date de création
- `acknowledged_at` (DateTimeField, nullable) - Date d'accusé de réception
- `resolved_at` (DateTimeField, nullable) - Date de résolution

**Méthodes**:
- `acknowledge()` - Marque l'alerte comme accusée réception
- `resolve()` - Marque l'alerte comme résolue
- `is_new()` - Vérifie si l'alerte est nouvelle
- `is_critical()` - Vérifie si l'alerte est critique

**Méthodes statiques (factory methods)**:
- `create_performance_alert(student, message, level='medium')`
- `create_attendance_alert(student, message, level='medium')`
- `create_risk_alert(student, message, level='high')`
- `create_prediction_alert(student, message, level='medium')`

**Propriétés**:
- `student_name` - Nom de l'étudiant
- `program_name` - Nom du programme de l'étudiant

---

## Relations entre les Modèles

### Diagramme des Relations Principales

```
User (auth)
  └─> (permissions) → can manage various entities

Program
  ├─> ManyToMany → Subject
  └─> OneToMany → Student

Session
  └─> OneToMany → Student

Student
  ├─> ForeignKey → Program
  ├─> ForeignKey → Session
  ├─> OneToMany → Grade
  ├─> OneToMany → Attendance
  ├─> OneToMany → Prediction
  └─> OneToMany → Alert

Subject
  ├─> ManyToMany → Program
  ├─> OneToMany → Grade
  └─> OneToMany → Attendance

MLModel
  └─> OneToMany → Prediction

Grade
  ├─> ForeignKey → Student
  ├─> ForeignKey → Subject
  └─> ForeignKey → Session

Attendance
  ├─> ForeignKey → Student
  └─> ForeignKey → Subject

Prediction
  ├─> ForeignKey → Student
  └─> ForeignKey → MLModel

Alert
  └─> ForeignKey → Student
```

## Indexes et Optimisations

Tous les modèles incluent des indexes stratégiques pour optimiser les requêtes:

- **Champs uniques**: Automatiquement indexés (matricule, email, code)
- **Champs de choix fréquents**: status, risk_level, type, level
- **Clés étrangères**: Automatiquement indexées
- **Champs de date**: Pour les requêtes chronologiques
- **Indexes composites**: Pour les requêtes multi-critères

## Validators

Les modèles utilisent les validators Django pour garantir l'intégrité des données:

- `MinValueValidator` / `MaxValueValidator` pour les scores (0-100)
- `EmailField` pour la validation des emails
- `unique=True` / `unique_together` pour l'unicité

## Bonnes Pratiques Implémentées

1. **Métadonnées temporelles**: `created_at` et `updated_at` sur tous les modèles
2. **Méthodes `__str__`**: Représentation lisible pour l'admin Django
3. **Properties calculées**: Pour les valeurs dérivées (student_count, percentage, etc.)
4. **Méthodes métier**: Logique applicative dans les modèles (activate, resolve, etc.)
5. **Choices avec TextChoices**: Type-safe choices avec Django 3.0+
6. **Help text**: Documentation inline pour l'admin
7. **Verbose names**: Labels traduits pour l'internationalisation
8. **Related names**: Navigation inverse facilitée
9. **On delete policies**: CASCADE, PROTECT selon le contexte
10. **Permissions personnalisées**: Contrôle d'accès granulaire

## Prochaines Étapes

1. **Migrations**: Exécuter `python manage.py makemigrations` puis `python manage.py migrate`
2. **Admin**: Configurer les classes ModelAdmin pour chaque modèle
3. **Serializers**: Créer les serializers DRF pour l'API REST
4. **ViewSets**: Implémenter les ViewSets pour les endpoints API
5. **Tests**: Écrire les tests unitaires pour chaque modèle
6. **Fixtures**: Créer des données de test

## Commandes Utiles

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Vérifier les modèles
python manage.py check
```

---

**Date de création**: 2026-01-02
**Version**: 1.0
**Auteur**: Backend Architecture Team
