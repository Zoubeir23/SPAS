import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import { studentService, Student } from '@/api/services/studentService'
import { predictionService } from '@/api/services/predictionService'
import { gradeService } from '@/api/services/gradeService'
import { attendanceService } from '@/api/services/attendanceService'
import { ROUTES } from '@/utils/constants'

type Tab = 'info' | 'grades' | 'attendance' | 'predictions'

export default function DetailEtudiant() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [student, setStudent] = useState<Student | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('info')
  const [loading, setLoading] = useState(true)
  const [grades, setGrades] = useState<any[]>([])
  const [attendance, setAttendance] = useState<any[]>([])
  const [prediction, setPrediction] = useState<any>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!id) return
      setLoading(true)
      try {
        const [studentData, gradesData, attendanceData, predictionData] = await Promise.all([
          studentService.getById(id),
          gradeService.getByStudent(id),
          attendanceService.getByStudent(id),
          predictionService.getByStudentId(id),
        ])
        setStudent(studentData)
        setGrades(gradesData)
        setAttendance(attendanceData)
        setPrediction(predictionData)
      } catch (error) {
        console.error('Erreur lors du chargement:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [id])

  if (loading) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500 dark:text-gray-400">Chargement...</div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  if (!student) {
    return (
      <MiseEnPagePrincipale>
        <div className="mx-auto max-w-7xl">
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Étudiant non trouvé
            </h2>
            <Bouton onClick={() => navigate(ROUTES.STUDENTS)}>Retour à la liste</Bouton>
          </div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  const getRiskBadge = () => {
    if (!student.riskLevel) {
      return (
        <Badge variant="success" className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[16px]">check_circle</span>
          <span className="uppercase tracking-wide">Normal</span>
        </Badge>
      )
    }

    switch (student.riskLevel) {
      case 'high':
        return (
          <Badge variant="danger" className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[16px]">warning</span>
            <span className="uppercase tracking-wide">Risque Élevé</span>
          </Badge>
        )
      case 'medium':
        return (
          <Badge variant="warning" className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[16px]">error</span>
            <span className="uppercase tracking-wide">Risque Moyen</span>
          </Badge>
        )
      default:
        return (
          <Badge variant="success" className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[16px]">check_circle</span>
            <span className="uppercase tracking-wide">Faible Risque</span>
          </Badge>
        )
    }
  }

  const tabs = [
    { id: 'info' as Tab, label: 'Informations', icon: 'info' },
    { id: 'grades' as Tab, label: 'Notes', icon: 'grading' },
    { id: 'attendance' as Tab, label: 'Absences', icon: 'event_busy' },
    { id: 'predictions' as Tab, label: 'Prédictions IA', icon: 'auto_awesome' },
  ]

  return (
    <MiseEnPagePrincipale
      title={`Fiche Étudiant - ${student.firstName} ${student.lastName}`}
      breadcrumbs={[
        { label: 'Accueil', path: ROUTES.DASHBOARD },
        { label: 'Étudiants', path: ROUTES.STUDENTS },
        { label: 'Fiche Profil' },
      ]}
    >
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        {/* Breadcrumbs & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex flex-wrap gap-2 items-center">
            <button
              onClick={() => navigate(ROUTES.STUDENTS)}
              className="text-gray-600 dark:text-gray-400 text-sm font-medium hover:text-primary transition-colors"
            >
              ← Retour
            </button>
          </div>
          <div className="flex items-center gap-3">
            <Bouton variant="outline" onClick={() => navigate(ROUTES.STUDENTS)}>
              <span className="material-symbols-outlined text-[20px]">arrow_back</span>
              Retour
            </Bouton>
            <Bouton>
              <span className="material-symbols-outlined text-[18px]">edit</span>
              Modifier
            </Bouton>
          </div>
        </div>

        {/* Student Summary Carte */}
        <Carte>
          <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
            <div className="relative group cursor-pointer shrink-0">
              <div className="size-24 md:size-28 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-bold text-2xl border-4 border-white dark:border-gray-700 shadow-md">
                {(student.firstName ?? 'X')[0]}
                {(student.lastName ?? 'X')[0]}
              </div>
            </div>
            <div className="flex-1 flex flex-col gap-1 w-full">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 w-full">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {student.firstName} {student.lastName}
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">
                    {student.programName} - {student.sessionName}
                  </p>
                </div>
                {getRiskBadge()}
              </div>
              <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-[18px]">badge</span>
                  <span>
                    Matricule:{' '}
                    <span className="text-gray-900 dark:text-white font-medium">
                      {student.matricule}
                    </span>
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <span className="material-symbols-outlined text-[18px]">mail</span>
                  <span>{student.email}</span>
                </div>
                {student.phone && (
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="material-symbols-outlined text-[18px]">call</span>
                    <span>{student.phone}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </Carte>

        {/* Tabs Navigation */}
        <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-surface-dark rounded-t-xl -mb-6 shadow-sm sticky top-0 z-10 px-6 pt-2">
          <nav className="flex gap-6 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`border-b-2 py-4 px-2 text-sm font-medium flex items-center gap-2 whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-200 dark:hover:border-gray-700'
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">{tab.icon}</span>
                {tab.label}
                {tab.id === 'attendance' && attendance.length > 0 && (
                  <span className="bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                    {attendance.length}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <Carte className="rounded-t-none">
          {activeTab === 'info' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12">
              {/* Personal Info */}
              <section className="flex flex-col gap-5">
                <div className="flex items-center gap-3 pb-2 border-b border-gray-200 dark:border-gray-800">
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-1.5 rounded text-primary">
                    <span className="material-symbols-outlined text-[20px]">person</span>
                  </div>
                  <h3 className="text-base font-bold text-gray-900 dark:text-white">
                    Informations Personnelles
                  </h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Date de naissance
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">
                      {student.dateOfBirth
                        ? new Date(student.dateOfBirth).toLocaleDateString('fr-FR')
                        : 'Non renseignée'}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Email
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{student.email}</p>
                  </div>
                  {student.phone && (
                    <div>
                      <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Téléphone
                      </label>
                      <p className="text-sm text-gray-900 dark:text-white mt-1">
                        {student.phone}
                      </p>
                    </div>
                  )}
                </div>
              </section>

              {/* Academic Info */}
              <section className="flex flex-col gap-5">
                <div className="flex items-center gap-3 pb-2 border-b border-gray-200 dark:border-gray-800">
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-1.5 rounded text-purple-600 dark:text-purple-400">
                    <span className="material-symbols-outlined text-[20px]">school</span>
                  </div>
                  <h3 className="text-base font-bold text-gray-900 dark:text-white">
                    Informations Académiques
                  </h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Filière
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">
                      {student.programName}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Session
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">
                      {student.sessionName}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Statut
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">
                      {student.status === 'active' ? 'Actif' : 'Inactif'}
                    </p>
                  </div>
                </div>
              </section>
            </div>
          )}

          {activeTab === 'grades' && (
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Notes</h3>
              {grades.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">Aucune note enregistrée</p>
              ) : (
                <div className="space-y-4">
                  {grades.map((grade) => (
                    <div
                      key={grade.id}
                      className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {grade.subjectName}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {grade.type} - {new Date(grade.date).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {grade.value}/{grade.maxValue}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {((grade.value / grade.maxValue) * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'attendance' && (
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Absences</h3>
              {attendance.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">Aucune absence enregistrée</p>
              ) : (
                <div className="space-y-4">
                  {attendance.map((att) => (
                    <div
                      key={att.id}
                      className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {new Date(att.date).toLocaleDateString('fr-FR')}
                        </p>
                        {att.subjectName && (
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {att.subjectName}
                          </p>
                        )}
                      </div>
                      <Badge
                        variant={
                          att.status === 'absent'
                            ? 'danger'
                            : att.status === 'late'
                            ? 'warning'
                            : 'info'
                        }
                      >
                        {att.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'predictions' && (
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                Prédictions IA
              </h3>
              {prediction ? (
                <div className="space-y-6">
                  <Carte>
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-900 dark:text-white">
                        Score de Risque
                      </h4>
                      <Badge
                        variant={
                          prediction.riskLevel === 'high' || prediction.riskLevel === 'critical'
                            ? 'danger'
                            : prediction.riskLevel === 'medium'
                            ? 'warning'
                            : 'success'
                        }
                      >
                        {prediction.riskScore}%
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Taux de réussite prédit: {prediction.predictedSuccessRate}%
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                      Modèle: {prediction.modelVersion} -{' '}
                      {new Date(prediction.createdAt).toLocaleDateString('fr-FR')}
                    </p>
                  </Carte>
                  {prediction.factors && prediction.factors.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                        Facteurs de Risque
                      </h4>
                      <div className="space-y-2">
                        {prediction.factors.map((factor: any, index: number) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                          >
                            <span className="text-sm text-gray-900 dark:text-white">
                              {factor.name}
                            </span>
                            <span
                              className={`text-sm font-medium ${
                                factor.impact < 0
                                  ? 'text-red-600 dark:text-red-400'
                                  : 'text-green-600 dark:text-green-400'
                              }`}
                            >
                              {factor.impact > 0 ? '+' : ''}
                              {(factor.impact * 100).toFixed(0)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">
                  Aucune prédiction disponible pour cet étudiant
                </p>
              )}
            </div>
          )}
        </Carte>
      </div>
    </MiseEnPagePrincipale>
  )
}
