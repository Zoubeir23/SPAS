import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface Attendance {
  id: string
  studentId?: string
  student_id?: string
  studentName?: string
  student_name?: string
  student?: { id: string; first_name: string; last_name: string }
  date: string
  status: 'present' | 'absent' | 'late' | 'excused'
  subjectId?: string
  subject_id?: string
  subjectName?: string
  subject_name?: string
  subject?: { id: string; name: string }
  justification?: string
  created_at?: string
  updated_at?: string
}

export interface AttendanceListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Attendance[]
}

export interface AttendanceFilters {
  student?: string
  subject?: string
  status?: string
  date_from?: string
  date_to?: string
  ordering?: string
  page?: number
  page_size?: number
}

/**
 * Normalize attendance data from API response
 */
function normalizeAttendance(attendance: Attendance): Attendance {
  return {
    ...attendance,
    studentId: attendance.studentId || attendance.student_id || attendance.student?.id,
    studentName: attendance.studentName || attendance.student_name ||
      (attendance.student ? `${attendance.student.first_name} ${attendance.student.last_name}` : undefined),
    subjectId: attendance.subjectId || attendance.subject_id || attendance.subject?.id,
    subjectName: attendance.subjectName || attendance.subject_name || attendance.subject?.name,
  }
}

/**
 * Attendance Service - Connected to Django REST Framework API
 */
export const attendanceService = {
  async getAll(filters?: AttendanceFilters): Promise<Attendance[]> {
    const response = await apiClient.get<AttendanceListResponse | Attendance[]>(
      API_ENDPOINTS.ATTENDANCE.BASE,
      { params: filters }
    )
    const records = Array.isArray(response.data) ? response.data : response.data.results
    return records.map(normalizeAttendance)
  },

  async getById(id: string): Promise<Attendance | null> {
    try {
      const response = await apiClient.get<Attendance>(API_ENDPOINTS.ATTENDANCE.BY_ID(id))
      return normalizeAttendance(response.data)
    } catch {
      return null
    }
  },

  async create(attendance: Partial<Attendance>): Promise<Attendance> {
    const payload = {
      student_id: attendance.studentId || attendance.student_id,
      subject_id: attendance.subjectId || attendance.subject_id,
      date: attendance.date,
      status: attendance.status,
      justification: attendance.justification,
    }
    const response = await apiClient.post<Attendance>(API_ENDPOINTS.ATTENDANCE.BASE, payload)
    return normalizeAttendance(response.data)
  },

  async update(id: string, updates: Partial<Attendance>): Promise<Attendance> {
    const payload: Record<string, unknown> = {}
    if (updates.status) payload.status = updates.status
    if (updates.justification !== undefined) payload.justification = updates.justification
    if (updates.date) payload.date = updates.date

    const response = await apiClient.patch<Attendance>(API_ENDPOINTS.ATTENDANCE.BY_ID(id), payload)
    return normalizeAttendance(response.data)
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.ATTENDANCE.BY_ID(id))
  },

  async getByStudent(studentId: string): Promise<Attendance[]> {
    const response = await apiClient.get<Attendance[]>(API_ENDPOINTS.ATTENDANCE.BY_STUDENT(studentId))
    return response.data.map(normalizeAttendance)
  },
}

