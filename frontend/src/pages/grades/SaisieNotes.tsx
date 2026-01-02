import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import Badge from '@/components/common/Badge'
import { studentService, Student } from '@/api/services/studentService'
import { sessionService } from '@/api/services/sessionService'
import { gradeService } from '@/api/services/gradeService'

interface GradeEntry {
  studentId: string
  studentName: string
  matricule: string
  value: string
  observation: string
  status: 'validated' | 'pending' | 'missing'
}

export default function SaisieNotes() {
  const [selectedSession, setSelectedSession] = useState('')
  const [selectedProgram, setSelectedProgram] = useState('')
  const [selectedSubject, setSelectedSubject] = useState('')
  const [students, setStudents] = useState<Student[]>([])
  const [sessions, setSessions] = useState<any[]>([])
  const [grades, setGrades] = useState<GradeEntry[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadSessions = async () => {
      const data = await sessionService.getAll()
      setSessions(data)
      if (data.length > 0 && !selectedSession) {
        setSelectedSession(data[0].id)
      }
    }
    loadSessions()
  }, [])

  useEffect(() => {
    const loadStudents = async () => {
      if (!selectedSession) return
      setLoading(true)
      try {
        const data = await studentService.getAll()
        const filtered = selectedProgram
          ? data.filter((s) => s.programId === selectedProgram)
          : data
        setStudents(filtered)
        setGrades(
          filtered.map((s) => ({
            studentId: s.id,
            studentName: `${s.firstName} ${s.lastName}`,
            matricule: s.matricule,
            value: '',
            observation: '',
            status: 'pending' as const,
          }))
        )
      } catch (error) {
        console.error('Erreur lors du chargement des étudiants:', error)
      } finally {
        setLoading(false)
      }
    }
    loadStudents()
  }, [selectedSession, selectedProgram])

  const handleGradeChange = (studentId: string, value: string) => {
    setGrades((prev) =>
      prev.map((g) => {
        if (g.studentId === studentId) {
          const numValue = parseFloat(value)
          const status =
            value === '' ? 'pending' : numValue >= 0 && numValue <= 20 ? 'validated' : 'pending'
          return { ...g, value, status }
        }
        return g
      })
    )
  }

  const handleObservationChange = (studentId: string, observation: string) => {
    setGrades((prev) => prev.map((g) => (g.studentId === studentId ? { ...g, observation } : g)))
  }

  const handleSubmit = async () => {
    try {
      for (const grade of grades) {
        if (grade.value) {
          await gradeService.create({
            studentId: grade.studentId,
            studentName: grade.studentName,
            subjectId: selectedSubject,
            subjectName: selectedSubject || 'Matière',
            sessionId: selectedSession,
            sessionName: sessions.find((s) => s.id === selectedSession)?.name || '',
            value: parseFloat(grade.value),
            maxValue: 20,
            type: 'exam',
            date: new Date().toISOString(),
          })
        }
      }
      alert('Notes enregistrées avec succès!')
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement:', error)
      alert('Erreur lors de l\'enregistrement des notes')
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const programs = ['Génie Logiciel - Gr. 01', 'Génie Logiciel - Gr. 02', 'Informatique de Gestion']
  const subjects = ['Base de données II', 'Algorithmique', 'Développement Web']

  return (
    <MiseEnPagePrincipale title="Saisie des Notes">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Page Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="flex flex-col gap-1">
            <h1 className="text-3xl md:text-4xl font-black leading-tight tracking-tight text-gray-900 dark:text-white">
              Saisie des Notes
            </h1>
            <p className="text-primary/80 text-base font-normal">
              Gestion des évaluations et résultats académiques
            </p>
          </div>
          <div className="hidden md:block">
            <div className="px-3 py-1 bg-primary/10 rounded-full border border-primary/20 text-primary text-xs font-bold uppercase tracking-wide">
              Mode Édition
            </div>
          </div>
        </div>

        {/* Filters & Context Selection */}
        <Carte>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Session</span>
              <div className="relative">
                <select
                  value={selectedSession}
                  onChange={(e) => setSelectedSession(e.target.value)}
                  className="w-full h-11 pl-4 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary focus:border-transparent appearance-none"
                >
                  <option value="">Sélectionner une session</option>
                  {sessions.map((session) => (
                    <option key={session.id} value={session.id}>
                      {session.name}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
                  <span className="material-symbols-outlined">expand_more</span>
                </div>
              </div>
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Filière</span>
              <div className="relative">
                <select
                  value={selectedProgram}
                  onChange={(e) => setSelectedProgram(e.target.value)}
                  className="w-full h-11 pl-4 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary focus:border-transparent appearance-none"
                >
                  <option value="">Toutes les filières</option>
                  {programs.map((program, index) => (
                    <option key={index} value={String(index + 1)}>
                      {program}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
                  <span className="material-symbols-outlined">expand_more</span>
                </div>
              </div>
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Matière</span>
              <div className="relative">
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="w-full h-11 pl-4 pr-10 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary focus:border-transparent appearance-none"
                >
                  <option value="">Sélectionner une matière</option>
                  {subjects.map((subject, index) => (
                    <option key={index} value={String(index + 1)}>
                      {subject}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
                  <span className="material-symbols-outlined">expand_more</span>
                </div>
              </div>
            </label>
          </div>
        </Carte>

        {/* Data Table Section */}
        <Carte className="overflow-hidden">
          {/* Toolbar */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
            <h3 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">groups</span>
              Liste des étudiants ({students.length})
            </h3>
            <div className="flex gap-2">
              <Bouton variant="outline" size="sm">
                <span className="material-symbols-outlined text-[18px]">filter_list</span>
                Filtres
              </Bouton>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 dark:bg-gray-700/50 text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  <th className="px-6 py-4 font-semibold border-b border-gray-200 dark:border-gray-700">
                    Matricule
                  </th>
                  <th className="px-6 py-4 font-semibold border-b border-gray-200 dark:border-gray-700">
                    Nom & Prénom
                  </th>
                  <th className="px-6 py-4 font-semibold border-b border-gray-200 dark:border-gray-700 w-[180px]">
                    Note (/20)
                  </th>
                  <th className="px-6 py-4 font-semibold border-b border-gray-200 dark:border-gray-700">
                    Observation
                  </th>
                  <th className="px-6 py-4 font-semibold border-b border-gray-200 dark:border-gray-700 text-center w-[80px]">
                    Statut
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700 text-sm">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                      Chargement...
                    </td>
                  </tr>
                ) : grades.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                      Aucun étudiant trouvé
                    </td>
                  </tr>
                ) : (
                  grades.map((grade) => (
                    <tr
                      key={grade.studentId}
                      className="group hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                    >
                      <td className="px-6 py-4 font-mono text-gray-500 dark:text-gray-400">
                        {grade.matricule}
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                        <div className="flex items-center gap-3">
                          <div className="size-8 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xs font-bold">
                            {getInitials(grade.studentName)}
                          </div>
                          <span>{grade.studentName}</span>
                        </div>
                      </td>
                      <td className="px-6 py-3">
                        <div className="relative">
                          <input
                            type="number"
                            min="0"
                            max="20"
                            step="0.1"
                            placeholder="0-20"
                            value={grade.value}
                            onChange={(e) => handleGradeChange(grade.studentId, e.target.value)}
                            className="block w-full rounded-lg border-gray-300 dark:border-gray-600 pl-3 pr-10 py-2 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-900 font-mono font-medium"
                          />
                          {grade.status === 'validated' && (
                            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                              <span className="material-symbols-outlined text-green-500 text-[18px]">
                                check_circle
                              </span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-3">
                        <input
                          type="text"
                          placeholder="Ajouter une observation..."
                          value={grade.observation}
                          onChange={(e) => handleObservationChange(grade.studentId, e.target.value)}
                          className="block w-full rounded-lg border-gray-300 dark:border-gray-600 px-3 py-2 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-900 text-sm placeholder:text-gray-400"
                        />
                      </td>
                      <td className="px-6 py-4 text-center">
                        {grade.status === 'validated' && (
                          <Badge variant="success" size="sm">
                            Validé
                          </Badge>
                        )}
                        {grade.status === 'pending' && grade.value && (
                          <Badge variant="warning" size="sm">
                            En attente
                          </Badge>
                        )}
                        {grade.status === 'pending' && !grade.value && (
                          <Badge variant="info" size="sm">
                            À saisir
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {grades.filter((g) => g.status === 'validated').length} / {grades.length} notes
              saisies
            </div>
            <div className="flex gap-3">
              <Bouton variant="outline">Annuler</Bouton>
              <Bouton onClick={handleSubmit}>
                <span className="material-symbols-outlined text-[18px] mr-2">save</span>
                Enregistrer les notes
              </Bouton>
            </div>
          </div>
        </Carte>
      </div>
    </MiseEnPagePrincipale>
  )
}
