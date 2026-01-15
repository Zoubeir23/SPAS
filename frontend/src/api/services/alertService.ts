import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Alert {
  id: string
  studentId?: string
  student_id?: string
  studentName?: string
  student_name?: string
  student?: { id: string; first_name: string; last_name: string }
  type: 'performance' | 'attendance' | 'risk' | 'prediction'
  level: 'low' | 'medium' | 'high' | 'critical'
  message: string
  status: 'new' | 'acknowledged' | 'resolved'
  createdAt?: string
  created_at?: string
  programName?: string
  program_name?: string
  program?: { id: string; name: string }
  acknowledged_at?: string
  resolved_at?: string
  acknowledged_by?: string
  resolved_by?: string
}

export interface AlertListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Alert[]
}

export interface AlertFilters {
  student?: string
  type?: string
  level?: string
  status?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface AlertStatistics {
  total: number
  new: number
  acknowledged: number
  resolved: number
  by_type: Record<string, number>
  by_level: Record<string, number>
}

/**
 * Normalize alert data from API response
 */
function normalizeAlert(alert: Alert): Alert {
  return {
    ...alert,
    studentId: alert.studentId || alert.student_id || alert.student?.id,
    studentName: alert.studentName || alert.student_name ||
      (alert.student ? `${alert.student.first_name} ${alert.student.last_name}` : undefined),
    createdAt: alert.createdAt || alert.created_at,
    programName: alert.programName || alert.program_name || alert.program?.name,
  }
}

/**
 * Alert Service - Connected to Django REST Framework API
 */
export const alertService = {
  async getAll(filters?: AlertFilters): Promise<Alert[]> {
    const response = await apiClient.get<AlertListResponse | Alert[]>(
      API_ENDPOINTS.ALERTS.BASE,
      { params: filters }
    )
    const alerts = Array.isArray(response.data) ? response.data : response.data.results
    return alerts.map(normalizeAlert)
  },

  async getById(id: string): Promise<Alert | null> {
    try {
      const response = await apiClient.get<Alert>(API_ENDPOINTS.ALERTS.BY_ID(id))
      return normalizeAlert(response.data)
    } catch {
      return null
    }
  },

  async acknowledge(id: string): Promise<Alert> {
    const response = await apiClient.post<Alert>(API_ENDPOINTS.ALERTS.ACKNOWLEDGE(id))
    return normalizeAlert(response.data)
  },

  async resolve(id: string): Promise<Alert> {
    const response = await apiClient.post<Alert>(API_ENDPOINTS.ALERTS.RESOLVE(id))
    return normalizeAlert(response.data)
  },

  async getUnread(): Promise<Alert[]> {
    const response = await apiClient.get<Alert[]>(API_ENDPOINTS.ALERTS.UNREAD)
    return response.data.map(normalizeAlert)
  },

  async getStatistics(): Promise<AlertStatistics> {
    const response = await apiClient.get<AlertStatistics>(API_ENDPOINTS.ALERTS.STATISTICS)
    return response.data
  },

  async getByType(): Promise<Record<string, Alert[]>> {
    const response = await apiClient.get<Record<string, Alert[]>>(API_ENDPOINTS.ALERTS.BY_TYPE)
    return response.data
  },

  async getByStudent(studentId: string): Promise<Alert[]> {
    const response = await apiClient.get<Alert[]>(API_ENDPOINTS.ALERTS.BY_STUDENT(studentId))
    return response.data.map(normalizeAlert)
  },

  async create(data: {
    student_id: string
    prediction_id?: string
    type: string
    message: string
    severity?: string
  }): Promise<Alert> {
    const response = await apiClient.post<Alert>(API_ENDPOINTS.ALERTS.BASE, {
      student: data.student_id,
      prediction: data.prediction_id,
      type: data.type,
      message: data.message,
      level: data.severity || 'medium',
      status: 'new'
    })
    return normalizeAlert(response.data)
  },
}

