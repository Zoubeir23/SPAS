import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Intervention {
  id: string
  student: string
  student_name?: string
  student_matricule?: string
  alert?: string
  type: 'meeting' | 'tutoring' | 'alert' | 'email' | 'phone' | 'parent_contact' | 'academic_support' | 'other'
  type_display?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  priority_display?: string
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled'
  status_display?: string
  description: string
  scheduled_date: string
  completed_date?: string
  responsible?: string
  responsible_name?: string
  notes?: string
  outcome?: string
  created_at?: string
  updated_at?: string
}

export interface InterventionListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Intervention[]
}

export interface CreateInterventionData {
  student: string
  alert?: string
  type: string
  priority: string
  description: string
  scheduled_date: string
  responsible?: string
}

export interface InterventionFilters {
  student?: string
  type?: string
  priority?: string
  status?: string
  responsible?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface InterventionStatistics {
  statistics: {
    total: number
    planned: number
    in_progress: number
    completed: number
    cancelled: number
  }
  type_distribution: Record<string, number>
}

/**
 * Intervention Service - Connected to Django REST Framework API
 */
export const interventionService = {
  async getAll(filters?: InterventionFilters): Promise<InterventionListResponse> {
    const response = await apiClient.get<InterventionListResponse>(
      API_ENDPOINTS.INTERVENTIONS.BASE, 
      { params: filters }
    )
    return response.data
  },

  async getById(id: string): Promise<Intervention> {
    const response = await apiClient.get<Intervention>(API_ENDPOINTS.INTERVENTIONS.BY_ID(id))
    return response.data
  },

  async create(data: CreateInterventionData): Promise<Intervention> {
    const response = await apiClient.post<Intervention>(API_ENDPOINTS.INTERVENTIONS.BASE, data)
    return response.data
  },

  async update(id: string, data: Partial<Intervention>): Promise<Intervention> {
    const response = await apiClient.patch<Intervention>(API_ENDPOINTS.INTERVENTIONS.BY_ID(id), data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.INTERVENTIONS.BY_ID(id))
  },

  async complete(id: string, outcome?: string): Promise<Intervention> {
    const response = await apiClient.post<{ data: Intervention }>(
      API_ENDPOINTS.INTERVENTIONS.COMPLETE(id),
      { outcome }
    )
    return response.data.data
  },

  async cancel(id: string): Promise<Intervention> {
    const response = await apiClient.post<{ data: Intervention }>(
      API_ENDPOINTS.INTERVENTIONS.CANCEL(id)
    )
    return response.data.data
  },

  async getByStudent(studentId: string): Promise<Intervention[]> {
    const response = await apiClient.get<Intervention[]>(
      API_ENDPOINTS.INTERVENTIONS.BY_STUDENT(studentId)
    )
    return response.data
  },

  async getPending(): Promise<Intervention[]> {
    const response = await apiClient.get<Intervention[]>(API_ENDPOINTS.INTERVENTIONS.PENDING)
    return response.data
  },

  async getStatistics(): Promise<InterventionStatistics> {
    const response = await apiClient.get<InterventionStatistics>(
      API_ENDPOINTS.INTERVENTIONS.STATISTICS
    )
    return response.data
  },
}

export default interventionService
