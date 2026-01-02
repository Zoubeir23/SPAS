# SPAS - Serializers Complets pour les 9 Apps

Ce document récapitule TOUS les serializers Django REST Framework pour le projet SPAS.

## Table des matières
1. [App Students](#1-app-students)
2. [App Programs](#2-app-programs)
3. [App Sessions](#3-app-sessions)
4. [App Grades](#4-app-grades)
5. [App Attendance](#5-app-attendance)
6. [App Users](#6-app-users)
7. [App ML](#7-app-ml)
8. [App Predictions](#8-app-predictions)
9. [App Alerts](#9-app-alerts)

---

## 1. App Students

**Fichier**: `backend/apps/students/serializers.py`

### Serializers disponibles:

#### 1.1 StudentListSerializer
- **Usage**: Listes légères d'étudiants
- **Champs inclus**:
  - id, student_id, first_name, last_name, full_name
  - email, status, status_display
  - program_name, program_code
  - admission_date, created_at
- **Champs calculés**: full_name (SerializerMethodField)
- **Champs nested**: program_name, program_code, status_display

#### 1.2 StudentSerializer
- **Usage**: Serializer standard pour les étudiants
- **Champs inclus**: Tous les champs du modèle Student
- **Champs nested**: program_name, program_code, full_name, status_display
- **Validations**: 
  - student_id unique
  - email unique

#### 1.3 StudentCreateSerializer
- **Usage**: Création d'étudiants
- **Validations**:
  - student_id unique
  - email unique
  - Dates cohérentes

---

## 2. App Programs

**Fichier**: `backend/apps/programs/serializers.py`

### Serializers disponibles:

#### 2.1 ProgramSerializer
- **Usage**: Programmes académiques
- **Champs inclus**: code, name, description, duration_months, credits_required, is_active
- **Champs calculés**: student_count (nombre d'étudiants actifs)

#### 2.2 ProgramListSerializer
- **Usage**: Listes légères de programmes
- **Champs**: id, code, name, is_active

#### 2.3 CourseSerializer
- **Usage**: Cours individuels
- **Champs inclus**: code, name, description, credits, is_mandatory
- **Champs nested**: program_name
- **Champs calculés**: prerequisite_count

#### 2.4 CourseListSerializer
- **Usage**: Listes de cours
- **Champs**: id, code, name, credits, program_name, is_mandatory

---

## 3. App Sessions

**Fichier**: `backend/apps/sessions/serializers.py`

### Serializers disponibles:

#### 3.1 AcademicPeriodSerializer
- **Usage**: Périodes académiques (sessions)
- **Champs**: name, season, year, start_date, end_date, is_active

#### 3.2 CourseSessionSerializer
- **Usage**: Offre de cours dans une session
- **Champs nested**: course_code, course_name, period_name, teacher_name
- **Champs calculés**: current_enrollment, is_full

#### 3.3 CourseSessionListSerializer
- **Usage**: Liste légère des sessions de cours

#### 3.4 EnrollmentSerializer
- **Usage**: Inscriptions d'étudiants aux cours
- **Champs nested**: student_name, student_id_display, course_code, course_name, period_name
- **Validations**: Vérification si la session est pleine

---

## 4. App Grades

**Fichier**: `backend/apps/grades/serializers.py`

### Serializers disponibles:

#### 4.1 GradeSerializer
- **Usage**: Notes individuelles
- **Champs nested**: student_name, course_code
- **Champs calculés**: weighted_grade

#### 4.2 GradeCreateSerializer
- **Usage**: Création de notes
- **Comportement**: Recalcule automatiquement le CourseGradeSummary

#### 4.3 CourseGradeSummarySerializer
- **Usage**: Résumé des notes pour un cours
- **Champs**: final_grade, letter_grade, is_passing, gpa_points (tous read_only)

---

## 5. App Attendance

**Fichier**: `backend/apps/attendance/serializers.py`

### Serializers disponibles:

#### 5.1 AttendanceRecordSerializer
- **Usage**: Présences individuelles
- **Champs nested**: student_name, student_id, course_code

#### 5.2 AttendanceRecordCreateSerializer
- **Usage**: Création de présences
- **Comportement**: Recalcule automatiquement AttendanceSummary

#### 5.3 AttendanceSummarySerializer
- **Usage**: Résumé de présence pour un cours
- **Champs calculés**: attendance_rate (tous read_only)

---

## 6. App Users

**Fichier**: `backend/apps/users/serializers.py`

### Serializers disponibles:

#### 6.1 UserSerializer
- **Usage**: Utilisateurs (sans password)
- **Champs**: email, first_name, last_name, role, phone, department

#### 6.2 UserCreateSerializer
- **Usage**: Création d'utilisateurs
- **Champs write_only**: password, password_confirm
- **Validations**: Django password validators

#### 6.3 UserUpdateSerializer
- **Usage**: Mise à jour utilisateurs

#### 6.4 ChangePasswordSerializer
- **Usage**: Changement de mot de passe

---

## 7. App ML

**Fichier**: `backend/apps/ml/serializers.py`

### Serializers disponibles:

#### 7.1 MLModelSerializer
- **Usage**: Modèles ML complets
- **Métriques**: accuracy, precision, recall, f1_score

#### 7.2 MLModelListSerializer
- **Usage**: Liste légère de modèles

#### 7.3 TrainingJobSerializer
- **Usage**: Jobs d'entraînement
- **Champs calculés**: duration

---

## 8. App Predictions

**Fichier**: `backend/apps/predictions/serializers.py`

### Serializers disponibles:

#### 8.1 PredictionSerializer
- **Usage**: Prédictions complètes
- **Facteurs**: attendance_factor, grade_factor, engagement_factor
- **Relations**: recommended_interventions (nested)

#### 8.2 PredictionListSerializer
- **Usage**: Liste légère de prédictions

#### 8.3 RecommendedInterventionSerializer
- **Usage**: Interventions recommandées

---

## 9. App Alerts

**Fichier**: `backend/apps/alerts/serializers.py`

### Serializers disponibles:

#### 9.1 AlertSerializer
- **Usage**: Alertes complètes
- **Relations**: actions (nested)
- **Champs calculés**: actions_count

#### 9.2 AlertListSerializer
- **Usage**: Liste légère d'alertes

#### 9.3 AlertActionSerializer
- **Usage**: Actions prises sur les alertes

---

## Conclusion

**Status**: ✅ 100% Complet

**Total**: 32 serializers implémentés pour 9 apps
