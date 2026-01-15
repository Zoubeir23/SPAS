import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface ROCCurve {
  fpr: number[]
  tpr: number[]
  thresholds?: number[]
}

export interface MLModel {
  id: string
  name: string
  version: string
  status: 'active' | 'inactive' | 'training' | 'archived'
  accuracy: number
  precision: number
  recall: number
  f1Score?: number
  f1_score?: number
  auc?: number
  trainedAt?: string
  trained_at?: string
  trainingDataSize?: number
  training_data_size?: number
  algorithm?: string
  description?: string
  created_at?: string
  updated_at?: string
  metrics?: {
    accuracy?: number
    precision?: number
    recall?: number
    f1_score?: number
    auc?: number
  }
  rocCurve?: ROCCurve
  roc_curve?: ROCCurve
  featureImportances?: Array<{ feature: string; importance: number }>
  feature_importances?: Array<{ feature: string; importance: number }>
  featureImportance?: Array<{ name: string; importance: number | string; category?: string }>
  confusionMatrix?: {
    tp: number  // True Positives
    tn: number  // True Negatives
    fp: number  // False Positives
    fn: number  // False Negatives
  }
  confusion_matrix?: {
    tp: number
    tn: number
    fp: number
    fn: number
  }
}

export interface MLModelListResponse {
  count: number
  next: string | null
  previous: string | null
  results: MLModel[]
}

export interface TrainingConfig {
  name: string
  trainingDataSize?: number
  training_data_size?: number
  description?: string
}

export interface ModelPerformance {
  model_id: string
  accuracy: number
  precision: number
  recall: number
  f1_score: number
  confusion_matrix?: number[][]
}

/**
 * Normalize MLModel data from API response
 */
function normalizeModel(model: MLModel): MLModel {
  return {
    ...model,
    f1Score: model.f1Score || model.f1_score,
    trainedAt: model.trainedAt || model.trained_at,
    trainingDataSize: model.trainingDataSize || model.training_data_size,
    auc: model.auc || model.metrics?.auc,
    rocCurve: model.rocCurve || model.roc_curve,
    featureImportances: model.featureImportances || model.feature_importances,
  }
}

/**
 * ML Service - Connected to Django REST Framework API
 */
export const mlService = {
  async getAll(): Promise<MLModel[]> {
    const response = await apiClient.get<MLModelListResponse | MLModel[]>(API_ENDPOINTS.ML.MODELS)
    const models = Array.isArray(response.data) ? response.data : response.data.results
    return models.map(normalizeModel)
  },

  async getById(id: string): Promise<MLModel | null> {
    try {
      const response = await apiClient.get<MLModel>(API_ENDPOINTS.ML.MODEL_BY_ID(id))
      return normalizeModel(response.data)
    } catch {
      return null
    }
  },

  async trainModel(config: TrainingConfig): Promise<MLModel> {
    const payload = {
      name: config.name,
      training_data_size: config.trainingDataSize || config.training_data_size,
      description: config.description,
    }
    const response = await apiClient.post<MLModel>(API_ENDPOINTS.ML.MODELS, payload)
    return normalizeModel(response.data)
  },

  async startTraining(id: string): Promise<MLModel> {
    const response = await apiClient.post<MLModel>(API_ENDPOINTS.ML.TRAIN(id))
    return normalizeModel(response.data)
  },

  async activate(id: string): Promise<MLModel> {
    const response = await apiClient.post<{ data: MLModel }>(`${API_ENDPOINTS.ML.MODEL_BY_ID(id)}/activate/`)
    return normalizeModel(response.data.data || response.data)
  },

  async deactivate(id: string): Promise<MLModel> {
    const response = await apiClient.patch<MLModel>(API_ENDPOINTS.ML.MODEL_BY_ID(id), {
      status: 'inactive',
    })
    return normalizeModel(response.data)
  },

  async archive(id: string): Promise<MLModel> {
    const response = await apiClient.post<{ data: MLModel }>(`${API_ENDPOINTS.ML.MODEL_BY_ID(id)}/archive/`)
    return normalizeModel(response.data.data || response.data)
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.ML.MODEL_BY_ID(id))
  },

  async getActiveModel(): Promise<MLModel | null> {
    try {
      const response = await apiClient.get<MLModel>(API_ENDPOINTS.ML.ACTIVE)
      return normalizeModel(response.data)
    } catch {
      return null
    }
  },

  async getPerformance(): Promise<ModelPerformance[]> {
    const response = await apiClient.get<ModelPerformance[]>(API_ENDPOINTS.ML.PERFORMANCE)
    return response.data
  },

  async getTrainingJobs(): Promise<any[]> {
    try {
      const response = await apiClient.get<any[]>(API_ENDPOINTS.ML.TRAINING_JOBS)
      return response.data
    } catch {
      return []
    }
  },
}

