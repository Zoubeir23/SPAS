import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import Alerte from '@/components/common/Alerte'
import { attendanceService } from '@/api/services/attendanceService'
import { studentService } from '@/api/services/studentService'
import { subjectService } from '@/api/services/programService'

interface AbsenceModalProps {
  isOpen: boolean
  onClose: () => void
  attendanceId?: string
  onSuccess?: () => void
}

export default function ModaleAbsence({
  isOpen,
  onClose,
  attendanceId,
  onSuccess,
}: AbsenceModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [students, setStudents] = useState<any[]>([])
  const [subjects, setSubjects] = useState<any[]>([])
  const [formData, setFormData] = useState({
    studentId: '',
    subjectId: '',
    date: new Date().toISOString().split('T')[0],
    status: 'absent' as 'present' | 'absent' | 'late' | 'excused',
    justification: '',
  })

  // Load students and subjects
  useEffect(() => {
    if (isOpen) {
      const loadData = async () => {
        try {
          const [studentsData, subjectsData] = await Promise.all([
            studentService.getAll(),
            subjectService.getAll(),
          ])
          
          // Les deux services retournent directement des arrays
          setStudents(studentsData)
          setSubjects(subjectsData)
        } catch (err) {
          console.error('Erreur lors du chargement des données:', err)
        }
      }
      loadData()
    }
  }, [isOpen])

  // Load attendance data if editing
  useEffect(() => {
    if (isOpen && attendanceId) {
      const loadAttendance = async () => {
        try {
          const attendance = await attendanceService.getById(attendanceId)
          if (attendance) {
            setFormData({
              studentId: attendance.studentId || attendance.student_id || '',
              subjectId: attendance.subjectId || attendance.subject_id || '',
              date: attendance.date,
              status: attendance.status,
              justification: attendance.justification || '',
            })
          }
        } catch (err) {
          console.error('Erreur lors du chargement de l\'absence:', err)
        }
      }
      loadAttendance()
    } else if (isOpen && !attendanceId) {
      // Reset form for new attendance
      setFormData({
        studentId: '',
        subjectId: '',
        date: new Date().toISOString().split('T')[0],
        status: 'absent',
        justification: '',
      })
      setError(null)
    }
  }, [isOpen, attendanceId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.studentId) {
      setError('Veuillez sélectionner un étudiant')
      return
    }
    
    if (!formData.subjectId) {
      setError('Veuillez sélectionner une matière')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      if (attendanceId) {
        await attendanceService.update(attendanceId, formData)
      } else {
        await attendanceService.create(formData)
      }
      onSuccess?.()
      onClose()
    } catch (err: any) {
      console.error('Erreur:', err)
      setError(
        err.response?.data?.detail || 
        err.response?.data?.message || 
        err.message || 
        'Une erreur est survenue lors de l\'enregistrement de l\'absence'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title={attendanceId ? 'Modifier l\'absence' : 'Saisir une absence'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <Alerte type="error" onClose={() => setError(null)}>
            {error}
          </Alerte>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2.5">
            Étudiant <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.studentId}
            onChange={(e) => setFormData({ ...formData, studentId: e.target.value })}
            className="block w-full rounded-lg border border-gray-300 bg-white dark:bg-surface-dark py-3 px-4 text-sm text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700"
            required
          >
            <option value="">Sélectionner un étudiant</option>
            {students.map((student) => (
              <option key={student.id} value={student.id}>
                {student.firstName || student.first_name} {student.lastName || student.last_name} - {student.matricule}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2.5">
            Matière <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.subjectId}
            onChange={(e) => setFormData({ ...formData, subjectId: e.target.value })}
            className="block w-full rounded-lg border border-gray-300 bg-white dark:bg-surface-dark py-3 px-4 text-sm text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700"
            required
          >
            <option value="">Sélectionner une matière</option>
            {subjects.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.name || subject.code}
              </option>
            ))}
          </select>
        </div>

        <ChampSaisie
          label="Date"
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          required
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2.5">
            Statut <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
            className="block w-full rounded-lg border border-gray-300 bg-white dark:bg-surface-dark py-3 px-4 text-sm text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700"
            required
          >
            <option value="present">Présent</option>
            <option value="absent">Absent</option>
            <option value="late">En retard</option>
            <option value="excused">Absence justifiée</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2.5">
            Justification
          </label>
          <textarea
            value={formData.justification}
            onChange={(e) => setFormData({ ...formData, justification: e.target.value })}
            rows={3}
            className="block w-full rounded-lg border border-gray-300 bg-white dark:bg-surface-dark py-3 px-4 text-sm text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700"
            placeholder="Justification de l'absence ou du retard (optionnel)"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Bouton
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={loading}
          >
            Annuler
          </Bouton>
          <Bouton
            type="submit"
            variant="primary"
            isLoading={loading}
            disabled={loading}
          >
            {attendanceId ? 'Modifier' : 'Enregistrer'}
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

