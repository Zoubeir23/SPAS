import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Session {
  id: string
  name: string
  year: string
  startDate?: string
  start_date?: string
  endDate?: string
  end_date?: string
  status: 'active' | 'inactive' | 'completed'
  studentCount?: number
  student_count?: number
  created_at?: string
  updated_at?: string
}

export interface SessionListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Session[]
}

export interface SessionFilters {
  search?: string
  status?: string
  year?: string
  ordering?: string
  page?: number
  page_size?: number
}

/**
 * Normalize session data from API response
 */
function normalizeSession(session: Session): Session {
  return {
    ...session,
    startDate: session.startDate || session.start_date,
    endDate: session.endDate || session.end_date,
    studentCount: session.studentCount || session.student_count || 0,
  }
}

/**
 * Session Service - Connected to Django REST Framework API
 */
export const sessionService = {
  async getAll(filters?: SessionFilters): Promise<Session[]> {
    const response = await apiClient.get<SessionListResponse | Session[]>(
      API_ENDPOINTS.SESSIONS.BASE,
      { params: filters }
    )
    const sessions = Array.isArray(response.data) ? response.data : response.data.results
    return sessions.map(normalizeSession)
  },

  async getById(id: string): Promise<Session | null> {
    try {
      const response = await apiClient.get<Session>(API_ENDPOINTS.SESSIONS.BY_ID(id))
      return normalizeSession(response.data)
    } catch {
      return null
    }
  },

  async create(session: Partial<Session>): Promise<Session> {
    const payload = {
      name: session.name,
      year: session.year,
      start_date: session.startDate || session.start_date,
      end_date: session.endDate || session.end_date,
      status: session.status || 'active',
    }
    const response = await apiClient.post<Session>(API_ENDPOINTS.SESSIONS.BASE, payload)
    return normalizeSession(response.data)
  },

  async update(id: string, updates: Partial<Session>): Promise<Session> {
    const payload: Record<string, unknown> = {}
    if (updates.name) payload.name = updates.name
    if (updates.year) payload.year = updates.year
    if (updates.startDate || updates.start_date) payload.start_date = updates.startDate || updates.start_date
    if (updates.endDate || updates.end_date) payload.end_date = updates.endDate || updates.end_date
    if (updates.status) payload.status = updates.status

    const response = await apiClient.patch<Session>(API_ENDPOINTS.SESSIONS.BY_ID(id), payload)
    return normalizeSession(response.data)
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.SESSIONS.BY_ID(id))
  },
}

