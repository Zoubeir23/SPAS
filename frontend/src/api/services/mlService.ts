import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface MLModel {
  id: string
  name: string
  version: string
  status: 'active' | 'inactive' | 'training'
  accuracy: number
  precision: number
  recall: number
  f1Score?: number
  f1_score?: number
  trainedAt?: string
  trained_at?: string
  trainingDataSize?: number
  training_data_size?: number
  description?: string
  created_at?: string
  updated_at?: string
  metrics?: {
    accuracy?: number
    precision?: number
    recall?: number
    f1_score?: number
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
    const response = await apiClient.patch<MLModel>(API_ENDPOINTS.ML.MODEL_BY_ID(id), {
      status: 'active',
    })
    return normalizeModel(response.data)
  },

  async deactivate(id: string): Promise<MLModel> {
    const response = await apiClient.patch<MLModel>(API_ENDPOINTS.ML.MODEL_BY_ID(id), {
      status: 'inactive',
    })
    return normalizeModel(response.data)
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

