# 🤖 Guide d'Utilisation du Modèle ML - SPAS

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Comment Utiliser le Modèle](#comment-utiliser-le-modèle)
3. [Intégration dans l'Application](#intégration-dans-lapplication)
4. [API Endpoints](#api-endpoints)
5. [Exemples d'Utilisation](#exemples-dutilisation)

---

## 🎯 Vue d'ensemble

Le modèle ML de SPAS utilise **XGBoost** pour prédire le risque de décrochage des étudiants. Il analyse 10 features clés pour générer un score de risque (0-100) et un niveau de risque (low, medium, high, critical).

### Features Analysées

1. **average_grade** - Moyenne des notes (0-20)
2. **attendance_rate** - Taux de présence (0-100%)
3. **assignments_completed** - Devoirs complétés (%)
4. **late_submissions** - Retards de soumission (nombre)
5. **absences_count** - Nombre total d'absences
6. **consecutive_absences** - Absences consécutives maximum
7. **grade_trend** - Tendance des notes (-1 à 1)
8. **participation_score** - Score de participation (0-100)
9. **weeks_enrolled** - Semaines depuis l'inscription
10. **failed_subjects** - Matières échouées (nombre)

### Niveaux de Risque

- **LOW** (0-25%) : Risque faible, étudiant en bonne voie
- **MEDIUM** (25-50%) : Risque modéré, surveillance recommandée
- **HIGH** (50-75%) : Risque élevé, intervention nécessaire
- **CRITICAL** (75-100%) : Risque critique, action urgente requise

---

## 🚀 Comment Utiliser le Modèle

### 1. Entraîner le Modèle

```bash
# Préparer les données depuis la base de données
python manage.py prepare_training_data --output ml_models/training_data.csv

# Entraîner le modèle
python manage.py train_model_from_data --data ml_models/training_data.csv --algorithm xgboost

# Activer le modèle
python manage.py activate_model 1.0.5
```

### 2. Utilisation en Python (Backend)

#### A. Prédiction pour un Étudiant

```python
from apps.ml.services import DropoutRiskPredictor, calculate_student_features_from_db
from apps.students.models import Student

# Initialiser le prédicteur
predictor = DropoutRiskPredictor()
predictor.load_model()  # Charge le modèle actif

# Obtenir un étudiant
student = Student.objects.get(id='...')

# Calculer les features
features = calculate_student_features_from_db(student)

# Faire la prédiction
prediction = predictor.predict_risk(features)

print(f"Score de risque: {prediction['risk_score']}%")
print(f"Niveau de risque: {prediction['risk_level']}")
print(f"Facteurs: {prediction['factors']}")
```

#### B. Prédiction en Masse

```python
from apps.students.models import Student
from apps.ml.services import DropoutRiskPredictor, calculate_student_features_from_db

predictor = DropoutRiskPredictor()
predictor.load_model()

students = Student.objects.filter(status='active')

for student in students:
    features = calculate_student_features_from_db(student)
    prediction = predictor.predict_risk(features)
    
    # Mettre à jour l'étudiant
    student.risk_score = prediction['risk_score']
    student.risk_level = prediction['risk_level']
    student.save(update_fields=['risk_score', 'risk_level'])
```

---

## 🔌 Intégration dans l'Application

### 1. Backend - API Endpoints

Le modèle est déjà intégré via les endpoints suivants :

#### A. Générer des Prédictions

**POST** `/api/predictions/generate/`

```json
{
  "student_ids": ["uuid1", "uuid2"]  // Optionnel, vide pour tous
}
```

**Réponse :**
```json
{
  "success": true,
  "predictions_created": 10,
  "alerts_created": 2,
  "predictions": [
    {
      "student_id": "uuid",
      "student_name": "Jean Dupont",
      "prediction_id": "uuid",
      "risk_score": 65.5,
      "risk_level": "high"
    }
  ]
}
```

#### B. Obtenir les Prédictions d'un Étudiant

**GET** `/api/predictions/student/{student_id}/`

**Réponse :**
```json
[
  {
    "id": "uuid",
    "student": "uuid",
    "risk_score": 65.5,
    "risk_level": "high",
    "predicted_success_rate": 34.5,
    "factors": [
      {
        "name": "average_grade",
        "value": 8.5,
        "impact": -15.2,
        "description": "Moyenne faible"
      }
    ],
    "created_at": "2026-01-03T20:00:00Z"
  }
]
```

#### C. Obtenir les Étudiants à Risque

**GET** `/api/predictions/at_risk/`

Retourne tous les étudiants avec `risk_level` HIGH ou CRITICAL.

#### D. Statistiques des Prédictions

**GET** `/api/predictions/statistics/`

**Réponse :**
```json
{
  "total_predictions": 100,
  "by_risk_level": {
    "low": 60,
    "medium": 25,
    "high": 12,
    "critical": 3
  },
  "average_risk_score": 32.5,
  "high_risk_count": 15
}
```

### 2. Frontend - Intégration React

#### A. Service API

Créer/modifier `frontend/src/api/services/predictionService.ts` :

```typescript
import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Prediction {
  id: string
  student: string
  risk_score: number
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  predicted_success_rate: number
  factors: RiskFactor[]
  created_at: string
}

export interface RiskFactor {
  name: string
  value: number
  impact: number
  description: string
}

export const predictionService = {
  // Générer des prédictions
  async generatePredictions(studentIds?: string[]): Promise<any> {
    const response = await apiClient.post(API_ENDPOINTS.PREDICTIONS.GENERATE, {
      student_ids: studentIds || []
    })
    return response.data
  },

  // Obtenir les prédictions d'un étudiant
  async getStudentPredictions(studentId: string): Promise<Prediction[]> {
    const response = await apiClient.get(
      `${API_ENDPOINTS.PREDICTIONS.BASE}student/${studentId}/`
    )
    return response.data
  },

  // Obtenir les étudiants à risque
  async getAtRiskStudents(): Promise<Prediction[]> {
    const response = await apiClient.get(API_ENDPOINTS.PREDICTIONS.AT_RISK)
    return response.data
  },

  // Obtenir les statistiques
  async getStatistics(): Promise<any> {
    const response = await apiClient.get(API_ENDPOINTS.PREDICTIONS.STATISTICS)
    return response.data
  },

  // Obtenir toutes les prédictions
  async getAll(): Promise<Prediction[]> {
    const response = await apiClient.get(API_ENDPOINTS.PREDICTIONS.BASE)
    return response.data
  }
}
```

#### B. Composant React - Affichage des Prédictions

```typescript
// frontend/src/components/predictions/PredictionCard.tsx
import { Prediction, RiskFactor } from '@/api/services/predictionService'
import Badge from '@/components/common/Badge'

interface PredictionCardProps {
  prediction: Prediction
}

export default function PredictionCard({ prediction }: PredictionCardProps) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'success'
      case 'medium': return 'warning'
      case 'high': return 'error'
      case 'critical': return 'error'
      default: return 'info'
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white dark:bg-surface-dark p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
          Prédiction de Risque
        </h3>
        <Badge variant={getRiskColor(prediction.risk_level)}>
          {prediction.risk_level.toUpperCase()}
        </Badge>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Score de Risque
          </span>
          <span className="text-2xl font-bold text-gray-900 dark:text-white">
            {prediction.risk_score}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all"
            style={{ width: `${prediction.risk_score}%` }}
          />
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Taux de Réussite Prédit
        </p>
        <p className="text-xl font-semibold text-gray-900 dark:text-white">
          {prediction.predicted_success_rate}%
        </p>
      </div>

      {prediction.factors && prediction.factors.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Facteurs de Risque Principaux
          </p>
          <ul className="space-y-2">
            {prediction.factors.slice(0, 3).map((factor, index) => (
              <li key={index} className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">
                  {factor.description}
                </span>
                <span className={`font-semibold ${
                  factor.impact > 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {factor.impact > 0 ? '+' : ''}{factor.impact.toFixed(1)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
```

#### C. Page de Dashboard Prédictif

```typescript
// frontend/src/pages/dashboard/TableauDeBordPredictif.tsx
import { useEffect, useState } from 'react'
import { predictionService, Prediction } from '@/api/services/predictionService'
import PredictionCard from '@/components/predictions/PredictionCard'

export default function TableauDeBordPredictif() {
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPredictions()
  }, [])

  const loadPredictions = async () => {
    try {
      const data = await predictionService.getAtRiskStudents()
      setPredictions(data)
    } catch (error) {
      console.error('Erreur lors du chargement des prédictions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePredictions = async () => {
    try {
      await predictionService.generatePredictions()
      await loadPredictions()
    } catch (error) {
      console.error('Erreur lors de la génération:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard Prédictif</h1>
        <button
          onClick={handleGeneratePredictions}
          className="px-4 py-2 bg-primary text-white rounded-lg"
        >
          Générer les Prédictions
        </button>
      </div>

      {loading ? (
        <p>Chargement...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {predictions.map((prediction) => (
            <PredictionCard key={prediction.id} prediction={prediction} />
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## 📊 Exemples d'Utilisation

### Exemple 1 : Générer des Prédictions pour Tous les Étudiants

```bash
# Via API
curl -X POST http://localhost:8000/api/predictions/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Exemple 2 : Obtenir les Prédictions d'un Étudiant

```bash
curl -X GET http://localhost:8000/api/predictions/student/{student_id}/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Exemple 3 : Utilisation dans une Vue Django

```python
# backend/apps/students/views.py
from apps.ml.services import DropoutRiskPredictor, calculate_student_features_from_db

class StudentDetailView(DetailView):
    model = Student
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Obtenir la prédiction
        predictor = DropoutRiskPredictor()
        predictor.load_model()
        
        features = calculate_student_features_from_db(student)
        prediction = predictor.predict_risk(features)
        
        context['prediction'] = prediction
        return context
```

---

## 🔄 Workflow Recommandé

### 1. Entraînement Initial
```bash
# Préparer les données
python manage.py prepare_training_data

# Entraîner
python manage.py train_model_from_data --algorithm xgboost

# Activer
python manage.py activate_model 1.0.5
```

### 2. Utilisation Quotidienne

1. **Générer les prédictions** (via API ou interface)
2. **Consulter le dashboard prédictif**
3. **Examiner les étudiants à risque**
4. **Créer des interventions** pour les étudiants HIGH/CRITICAL

### 3. Réentraînement Périodique

- **Fréquence recommandée** : Tous les 3-6 mois
- **Quand réentraîner** :
  - Nouveaux étudiants ajoutés
  - Changements dans les données historiques
  - Performance du modèle en baisse

---

## ⚠️ Notes Importantes

1. **Modèle Actif** : Seul le modèle avec `status='active'` est utilisé
2. **Features Manquantes** : Si une feature est manquante, elle est remplacée par 0
3. **Performance** : Le modèle actuel a 100% d'accuracy (peut être dû au petit dataset)
4. **SHAP** : Les explications SHAP sont disponibles si le modèle a été entraîné avec SHAP

---

## 🐛 Dépannage

### Le modèle ne se charge pas
```python
# Vérifier qu'un modèle actif existe
from apps.ml.models import MLModel
active = MLModel.objects.filter(status='active').first()
print(active)
```

### Prédictions incorrectes
- Vérifier que les features sont correctement calculées
- Vérifier que le modèle actif correspond aux données
- Réentraîner avec plus de données

### Erreur "Model file not found"
- Vérifier que le fichier `.joblib` existe dans `ml_models/`
- Réentraîner le modèle si nécessaire

