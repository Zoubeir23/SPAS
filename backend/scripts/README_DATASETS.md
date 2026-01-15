# 📊 Guide d'Intégration des Datasets pour SPAS

Ce guide explique comment télécharger et intégrer les datasets recommandés pour entraîner les modèles ML de SPAS.

## 🎯 Datasets Recommandés

### 1. 🥇 Kaggle Higher Education Dropout (PRINCIPAL)
- **URL**: https://www.kaggle.com/datasets/thedevastator/higher-education-predictors-of-student-retention
- **Taille**: 4424 étudiants
- **Features**: 37
- **Target**: Dropout / Enrolled / Graduate
- **Pourquoi**: Données réelles universitaires, features similaires à SPAS

### 2. 🥈 UCI Student Performance
- **URL**: https://archive.ics.uci.edu/ml/datasets/Student+Performance
- **Taille**: 649 étudiants
- **Features**: 33
- **Pourquoi**: Dataset académique validé, utilisé dans recherches

### 3. 🥉 Kaggle Student Performance in Exams
- **URL**: https://www.kaggle.com/datasets/spscientist/students-performance-in-exams
- **Taille**: 1000 étudiants
- **Features**: 8
- **Pourquoi**: Simple, bon pour débuter

### 4. ➕ xAPI-Edu-Data
- **URL**: https://www.kaggle.com/datasets/aljarah/xAPI-Edu-Data
- **Taille**: 480 étudiants
- **Features**: 17 (comportementales)
- **Pourquoi**: Comportement e-learning, absences, participation

---

## 🚀 Installation

### 1. Installer les dépendances

```bash
cd backend
pip install kaggle pandas numpy
```

### 2. Configurer Kaggle API

1. Aller sur https://www.kaggle.com/settings
2. Cliquer sur "Create New API Token"
3. Télécharger `kaggle.json`
4. Placer le fichier dans :
   - **Windows**: `C:\Users\<username>\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json`

### 3. Télécharger les datasets

```bash
# Depuis la racine du projet
python backend/scripts/download_datasets.py
```

Ou télécharger manuellement depuis les URLs ci-dessus.

---

## 📥 Utilisation

### Télécharger les datasets

```bash
python backend/scripts/download_datasets.py
```

Les datasets seront téléchargés dans le dossier `datasets/` à la racine du projet.

### Préparer les données d'entraînement depuis la base de données

```bash
cd backend
python manage.py prepare_training_data --output ml_models/training_data.csv
```

Cette commande :
- Extrait les features de tous les étudiants actifs
- Calcule les labels basés sur le risk_score
- Sauvegarde en CSV et/ou format numpy

### Charger des datasets externes (optionnel)

```bash
python manage.py load_training_data --dataset kaggle_dropout --limit 100
```

---

## 🔄 Workflow Recommandé

### Phase 1 : Données Réelles (Recommandé)
1. Utiliser les données réelles de votre base SPAS
2. Exécuter `prepare_training_data` pour créer le dataset
3. Entraîner le modèle avec ces données

### Phase 2 : Enrichissement avec Datasets Externes
1. Télécharger les datasets Kaggle/UCI
2. Mapper les features vers le format SPAS
3. Fusionner avec vos données réelles
4. Réentraîner le modèle

---

## 📋 Mapping des Features

Les datasets externes doivent être mappés vers les 10 features attendues par SPAS :

| Feature SPAS | Description | Source Possible |
|--------------|-------------|-----------------|
| `average_grade` | Moyenne des notes | Notes du dataset |
| `attendance_rate` | Taux de présence | Absences du dataset |
| `assignments_completed` | Devoirs complétés | Assignments/Homework |
| `late_submissions` | Soumissions en retard | Submission dates |
| `absences_count` | Nombre d'absences | Attendance records |
| `consecutive_absences` | Absences consécutives | Calculé |
| `grade_trend` | Tendance des notes | Calculé (pente) |
| `participation_score` | Score de participation | Participation/Engagement |
| `weeks_enrolled` | Semaines d'inscription | Date d'inscription |
| `failed_subjects` | Matières échouées | Notes < seuil |

---

## ⚠️ Considérations Importantes

### 1. Droits d'utilisation
- ✅ Tous les datasets proposés sont open source
- ✅ Utilisables pour projets académiques
- ⚠️ Vérifier licences si usage commercial futur

### 2. Qualité des données
- Vérifier valeurs manquantes
- Analyser distribution classes (équilibrage)
- Supprimer outliers extrêmes

### 3. Compatibilité SPAS
- Mapper features vers vos 24 features
- Créer features manquantes (feature engineering)
- Normaliser nomenclature (âge, genre, etc.)

---

## 📚 Ressources Complémentaires

- **Feature Engineering**: https://www.kaggle.com/learn/feature-engineering
- **Handling Imbalanced Data**: https://imbalanced-learn.org/stable/
- **Papers de référence**: Rechercher "Early Prediction of Student Success" sur Google Scholar

---

## 🐛 Dépannage

### Erreur: "Kaggle API not found"
```bash
pip install kaggle
# Vérifier que ~/.kaggle/kaggle.json existe
```

### Erreur: "Dataset not found"
- Vérifier que les datasets sont téléchargés dans `datasets/`
- Vérifier les noms de fichiers CSV

### Erreur: "No students found"
- S'assurer qu'il y a des étudiants actifs dans la base
- Vérifier que les étudiants ont des notes/absences

---

## 📝 Notes

- Les datasets sont stockés dans `datasets/` (non versionné dans git)
- Les données préparées sont dans `backend/ml_models/`
- Utiliser `--limit` pour tester avec un petit échantillon

