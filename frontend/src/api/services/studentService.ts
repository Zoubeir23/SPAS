import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Student {
  id: string
  matricule: string
  firstName?: string
  lastName?: string
  first_name?: string
  last_name?: string
  email: string
  phone?: string
  dateOfBirth?: string
  date_of_birth?: string
  programId?: string
  program_id?: string
  programName?: string
  program_name?: string
  program?: { id: string; name: string }
  sessionId?: string
  session_id?: string
  sessionName?: string
  session_name?: string
  session?: { id: string; name: string }
  status: 'active' | 'inactive' | 'graduated'
  level?: 'L1' | 'L2' | 'L3' | 'M1' | 'M2'
  level_display?: string
  riskLevel?: 'low' | 'medium' | 'high' | 'critical'
  risk_level?: 'low' | 'medium' | 'high' | 'critical'
  riskScore?: number
  risk_score?: number
  photo?: string
  photo_url?: string
  created_at?: string
  updated_at?: string
}

export interface StudentListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Student[]
}

export interface StudentFilters {
  search?: string
  status?: string
  program?: string
  session?: string
  risk_level?: string
  ordering?: string
  page?: number
  page_size?: number
}

/**
 * Normalize student data from API response
 */
function normalizeStudent(student: Student): Student {
  return {
    ...student,
    firstName: student.firstName || student.first_name,
    lastName: student.lastName || student.last_name,
    dateOfBirth: student.dateOfBirth || student.date_of_birth,
    programId: student.programId || student.program_id || student.program?.id,
    programName: student.programName || student.program_name || student.program?.name,
    sessionId: student.sessionId || student.session_id || student.session?.id,
    sessionName: student.sessionName || student.session_name || student.session?.name,
    riskLevel: student.riskLevel || student.risk_level,
    riskScore: student.riskScore || student.risk_score,
  }
}

/**
 * Student Service - Connected to Django REST Framework API
 */
export const studentService = {
  async getAll(filters?: StudentFilters): Promise<Student[]> {
    const response = await apiClient.get<StudentListResponse | Student[]>(
      API_ENDPOINTS.STUDENTS.BASE,
      { params: filters }
    )
    // Handle both paginated and non-paginated responses
    const students = Array.isArray(response.data) ? response.data : response.data.results
    return students.map(normalizeStudent)
  },

  async getById(id: string): Promise<Student | null> {
    try {
      const response = await apiClient.get<Student>(API_ENDPOINTS.STUDENTS.BY_ID(id))
      return normalizeStudent(response.data)
    } catch {
      return null
    }
  },

  async create(student: Partial<Student>): Promise<Student> {
    const payload = {
      matricule: student.matricule,
      first_name: student.firstName || student.first_name,
      last_name: student.lastName || student.last_name,
      email: student.email,
      phone: student.phone,
      date_of_birth: student.dateOfBirth || student.date_of_birth,
      program_id: student.programId || student.program_id,
      session_id: student.sessionId || student.session_id,
      status: student.status || 'active',
    }
    const response = await apiClient.post<Student>(API_ENDPOINTS.STUDENTS.BASE, payload)
    return normalizeStudent(response.data)
  },

  async update(id: string, updates: Partial<Student>): Promise<Student> {
    const payload: Record<string, unknown> = {}
    if (updates.matricule) payload.matricule = updates.matricule
    if (updates.firstName || updates.first_name) payload.first_name = updates.firstName || updates.first_name
    if (updates.lastName || updates.last_name) payload.last_name = updates.lastName || updates.last_name
    if (updates.email) payload.email = updates.email
    if (updates.phone) payload.phone = updates.phone
    if (updates.dateOfBirth || updates.date_of_birth) payload.date_of_birth = updates.dateOfBirth || updates.date_of_birth
    if (updates.programId || updates.program_id) payload.program_id = updates.programId || updates.program_id
    if (updates.sessionId || updates.session_id) payload.session_id = updates.sessionId || updates.session_id
    if (updates.status) payload.status = updates.status

    const response = await apiClient.patch<Student>(API_ENDPOINTS.STUDENTS.BY_ID(id), payload)
    return normalizeStudent(response.data)
  },

  async uploadPhoto(id: string, file: File): Promise<Student> {
    const formData = new FormData()
    formData.append('photo', file)
    const response = await apiClient.patch<Student>(
      API_ENDPOINTS.STUDENTS.BY_ID(id),
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return normalizeStudent(response.data)
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.STUDENTS.BY_ID(id))
  },

  async getAtRisk(): Promise<Student[]> {
    const response = await apiClient.get<Student[]>(API_ENDPOINTS.STUDENTS.AT_RISK)
    return response.data.map(normalizeStudent)
  },

  /**
   * Export all students to CSV file
   * @returns Blob of CSV file
   */
  async exportCsv(): Promise<Blob> {
    const response = await apiClient.get(API_ENDPOINTS.STUDENTS.EXPORT_CSV, {
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * Download students CSV export
   */
  async downloadCsv(): Promise<void> {
    const blob = await this.exportCsv()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'etudiants.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },

  /**
   * Import students from CSV file
   * @param file CSV file to import
   */
  async importCsv(file: File): Promise<{
    success: boolean
    message: string
    created: number
    updated: number
    errors: string[]
  }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post(API_ENDPOINTS.STUDENTS.IMPORT_CSV, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

