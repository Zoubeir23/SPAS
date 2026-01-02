import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Program {
  id: string
  name: string
  code: string
  description?: string
  duration: number // en années
  studentCount?: number
  student_count?: number
  status: 'active' | 'inactive'
  created_at?: string
  updated_at?: string
}

export interface ProgramListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Program[]
}

export interface ProgramFilters {
  search?: string
  status?: string
  ordering?: string
  page?: number
  page_size?: number
}

/**
 * Normalize program data from API response
 */
function normalizeProgram(program: Program): Program {
  return {
    ...program,
    studentCount: program.studentCount || program.student_count || 0,
  }
}

/**
 * Program Service - Connected to Django REST Framework API
 */
export const programService = {
  async getAll(filters?: ProgramFilters): Promise<Program[]> {
    const response = await apiClient.get<ProgramListResponse | Program[]>(
      API_ENDPOINTS.PROGRAMS.BASE,
      { params: filters }
    )
    const programs = Array.isArray(response.data) ? response.data : response.data.results
    return programs.map(normalizeProgram)
  },

  async getById(id: string): Promise<Program | null> {
    try {
      const response = await apiClient.get<Program>(API_ENDPOINTS.PROGRAMS.BY_ID(id))
      return normalizeProgram(response.data)
    } catch {
      return null
    }
  },

  async create(program: Omit<Program, 'id'>): Promise<Program> {
    const response = await apiClient.post<Program>(API_ENDPOINTS.PROGRAMS.BASE, program)
    return normalizeProgram(response.data)
  },

  async update(id: string, updates: Partial<Program>): Promise<Program> {
    const response = await apiClient.patch<Program>(API_ENDPOINTS.PROGRAMS.BY_ID(id), updates)
    return normalizeProgram(response.data)
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.PROGRAMS.BY_ID(id))
  },
}

/**
 * Subject interface and service
 */
export interface Subject {
  id: string
  name: string
  code: string
  program?: string
  program_id?: string
  credits?: number
  description?: string
}

export const subjectService = {
  async getAll(): Promise<Subject[]> {
    const response = await apiClient.get<Subject[]>(API_ENDPOINTS.SUBJECTS.BASE)
    return response.data
  },

  async getById(id: string): Promise<Subject | null> {
    try {
      const response = await apiClient.get<Subject>(API_ENDPOINTS.SUBJECTS.BY_ID(id))
      return response.data
    } catch {
      return null
    }
  },

  async create(subject: Omit<Subject, 'id'>): Promise<Subject> {
    const response = await apiClient.post<Subject>(API_ENDPOINTS.SUBJECTS.BASE, subject)
    return response.data
  },

  async update(id: string, updates: Partial<Subject>): Promise<Subject> {
    const response = await apiClient.patch<Subject>(API_ENDPOINTS.SUBJECTS.BY_ID(id), updates)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.SUBJECTS.BY_ID(id))
  },
}

