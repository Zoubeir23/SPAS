import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Grade {
  id: string
  studentId?: string
  student_id?: string
  studentName?: string
  student_name?: string
  student?: { id: string; first_name: string; last_name: string }
  subjectId?: string
  subject_id?: string
  subjectName?: string
  subject_name?: string
  subject?: { id: string; name: string }
  sessionId?: string
  session_id?: string
  sessionName?: string
  session_name?: string
  session?: { id: string; name: string }
  value: number
  maxValue?: number
  max_value?: number
  type: 'exam' | 'assignment' | 'project' | 'participation'
  date: string
  created_at?: string
  updated_at?: string
}

export interface GradeListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Grade[]
}

export interface GradeFilters {
  student?: string
  subject?: string
  session?: string
  type?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface GradeStatistics {
  average: number
  min: number
  max: number
  count: number
}

/**
 * Normalize grade data from API response
 */
function normalizeGrade(grade: Grade): Grade {
  return {
    ...grade,
    studentId: grade.studentId || grade.student_id || grade.student?.id,
    studentName: grade.studentName || grade.student_name || 
      (grade.student ? `${grade.student.first_name} ${grade.student.last_name}` : undefined),
    subjectId: grade.subjectId || grade.subject_id || grade.subject?.id,
    subjectName: grade.subjectName || grade.subject_name || grade.subject?.name,
    sessionId: grade.sessionId || grade.session_id || grade.session?.id,
    sessionName: grade.sessionName || grade.session_name || grade.session?.name,
    maxValue: grade.maxValue || grade.max_value || 100,
  }
}

/**
 * Grade Service - Connected to Django REST Framework API
 */
export const gradeService = {
  async getAll(filters?: GradeFilters): Promise<Grade[]> {
    const response = await apiClient.get<GradeListResponse | Grade[]>(
      API_ENDPOINTS.GRADES.BASE,
      { params: filters }
    )
    const grades = Array.isArray(response.data) ? response.data : response.data.results
    return grades.map(normalizeGrade)
  },

  async getById(id: string): Promise<Grade | null> {
    try {
      const response = await apiClient.get<Grade>(API_ENDPOINTS.GRADES.BY_ID(id))
      return normalizeGrade(response.data)
    } catch {
      return null
    }
  },

  async create(grade: Partial<Grade>): Promise<Grade> {
    const payload = {
      student_id: grade.studentId || grade.student_id,
      subject_id: grade.subjectId || grade.subject_id,
      session_id: grade.sessionId || grade.session_id,
      value: grade.value,
      max_value: grade.maxValue || grade.max_value || 100,
      type: grade.type,
      date: grade.date,
    }
    const response = await apiClient.post<Grade>(API_ENDPOINTS.GRADES.BASE, payload)
    return normalizeGrade(response.data)
  },

  async update(id: string, updates: Partial<Grade>): Promise<Grade> {
    const payload: Record<string, unknown> = {}
    if (updates.value !== undefined) payload.value = updates.value
    if (updates.maxValue || updates.max_value) payload.max_value = updates.maxValue || updates.max_value
    if (updates.type) payload.type = updates.type
    if (updates.date) payload.date = updates.date

    const response = await apiClient.patch<Grade>(API_ENDPOINTS.GRADES.BY_ID(id), payload)
    return normalizeGrade(response.data)
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.GRADES.BY_ID(id))
  },

  async getByStudent(studentId: string): Promise<Grade[]> {
    const response = await apiClient.get<Grade[]>(API_ENDPOINTS.GRADES.BY_STUDENT(studentId))
    return response.data.map(normalizeGrade)
  },

  async bulkCreate(grades: Partial<Grade>[]): Promise<Grade[]> {
    const payload = grades.map(g => ({
      student_id: g.studentId || g.student_id,
      subject_id: g.subjectId || g.subject_id,
      session_id: g.sessionId || g.session_id,
      value: g.value,
      max_value: g.maxValue || g.max_value || 100,
      type: g.type,
      date: g.date,
    }))
    const response = await apiClient.post<Grade[]>(API_ENDPOINTS.GRADES.BULK_CREATE, payload)
    return response.data.map(normalizeGrade)
  },

  async getStatistics(): Promise<GradeStatistics> {
    const response = await apiClient.get<GradeStatistics>(API_ENDPOINTS.GRADES.STATISTICS)
    return response.data
  },

  /**
   * Export grades to CSV file
   * @param filters Optional filters (student, subject, session)
   * @returns Blob of CSV file
   */
  async exportCsv(filters?: { student?: string; subject?: string; session?: string }): Promise<Blob> {
    const response = await apiClient.get(API_ENDPOINTS.GRADES.EXPORT_CSV, {
      params: filters,
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * Download grades CSV export
   */
  async downloadCsv(filters?: { student?: string; subject?: string; session?: string }): Promise<void> {
    const blob = await this.exportCsv(filters)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'notes.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },

  /**
   * Import grades from CSV file
   * @param file CSV file to import
   */
  async importCsv(file: File): Promise<{
    success: boolean
    message: string
    created: number
    errors: string[]
  }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post(API_ENDPOINTS.GRADES.IMPORT_CSV, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}

