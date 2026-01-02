import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface PredictionFactor {
  name: string
  impact: number
}

export interface Prediction {
  id: string
  studentId?: string
  student_id?: string
  studentName?: string
  student_name?: string
  student?: { id: string; first_name: string; last_name: string }
  riskScore?: number
  risk_score?: number
  riskLevel?: 'low' | 'medium' | 'high' | 'critical'
  risk_level?: 'low' | 'medium' | 'high' | 'critical'
  predictedSuccessRate?: number
  predicted_success_rate?: number
  factors?: PredictionFactor[]
  createdAt?: string
  created_at?: string
  modelVersion?: string
  model_version?: string
  model?: { id: string; version: string }
}

export interface PredictionListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Prediction[]
}

export interface PredictionFilters {
  student?: string
  risk_level?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface PredictionStatistics {
  total: number
  high_risk: number
  medium_risk: number
  low_risk: number
  average_score: number
}

export interface RiskDistribution {
  low: number
  medium: number
  high: number
  critical: number
}

/**
 * Normalize prediction data from API response
 */
function normalizePrediction(prediction: Prediction): Prediction {
  return {
    ...prediction,
    studentId: prediction.studentId || prediction.student_id || prediction.student?.id,
    studentName: prediction.studentName || prediction.student_name ||
      (prediction.student ? `${prediction.student.first_name} ${prediction.student.last_name}` : undefined),
    riskScore: prediction.riskScore || prediction.risk_score,
    riskLevel: prediction.riskLevel || prediction.risk_level,
    predictedSuccessRate: prediction.predictedSuccessRate || prediction.predicted_success_rate,
    createdAt: prediction.createdAt || prediction.created_at,
    modelVersion: prediction.modelVersion || prediction.model_version || prediction.model?.version,
  }
}

/**
 * Prediction Service - Connected to Django REST Framework API
 */
export const predictionService = {
  async getAll(filters?: PredictionFilters): Promise<Prediction[]> {
    const response = await apiClient.get<PredictionListResponse | Prediction[]>(
      API_ENDPOINTS.PREDICTIONS.BASE,
      { params: filters }
    )
    const predictions = Array.isArray(response.data) ? response.data : response.data.results
    return predictions.map(normalizePrediction)
  },

  async getById(id: string): Promise<Prediction | null> {
    try {
      const response = await apiClient.get<Prediction>(API_ENDPOINTS.PREDICTIONS.BY_ID(id))
      return normalizePrediction(response.data)
    } catch {
      return null
    }
  },

  async getByStudentId(studentId: string): Promise<Prediction | null> {
    try {
      const response = await apiClient.get<Prediction>(API_ENDPOINTS.PREDICTIONS.BY_STUDENT(studentId))
      return normalizePrediction(response.data)
    } catch {
      return null
    }
  },

  async getHighRisk(): Promise<Prediction[]> {
    const response = await apiClient.get<Prediction[]>(API_ENDPOINTS.PREDICTIONS.HIGH_RISK)
    return response.data.map(normalizePrediction)
  },

  async getStatistics(): Promise<PredictionStatistics> {
    const response = await apiClient.get<PredictionStatistics>(API_ENDPOINTS.PREDICTIONS.STATISTICS)
    return response.data
  },

  async getDistribution(): Promise<RiskDistribution> {
    const response = await apiClient.get<RiskDistribution>(API_ENDPOINTS.PREDICTIONS.DISTRIBUTION)
    return response.data
  },
}

