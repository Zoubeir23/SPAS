import { useEffect, useState } from 'react'
import { clsx } from 'clsx'
import { Link } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Badge from '@/components/common/Badge'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import GraphiqueCirculaire from '@/components/charts/GraphiqueCirculaire'
import { studentService } from '@/api/services/studentService'
import { programService } from '@/api/services/programService'
import { sessionService } from '@/api/services/sessionService'
import { alertService } from '@/api/services/alertService'
import { analyticsService, type EnrollmentEvolution } from '@/api/services/analyticsService'
import { predictionService } from '@/api/services/predictionService'
import { mlService } from '@/api/services/mlService'
import { userService } from '@/api/services/userService'
import { exportDashboardToPDF, type ExportColumn } from '@/utils/exportService'
import { useAuthStore } from '@/store/authStore'

interface DashboardStats {
  totalStudents: number
  activePrograms: number
  sessions: number
  successRate: number
}

interface ProgramDistributionItem {
  name: string
  value: number
}

// Types pour les données spécifiques par rôle
interface RoleSpecificData {
  // Pour enseignant
  myStudentsCount?: number
  myCoursesCount?: number
  pendingGrades?: number
  // Pour Data Scientist
  activeModels?: number
  totalPredictions?: number
  highRiskStudents?: number
  modelAccuracy?: number | null  // null = no model available
  hasActiveModel?: boolean
  // Pour Pédagogique
  openAlerts?: number
  pendingInterventions?: number
  atRiskStudents?: number
  // Pour Admin
  totalUsers?: number
  systemHealth?: string
}

export default function TableauDeBordGeneral() {
  const { user } = useAuthStore()
  const userRole = user?.role || 'teacher'
  
  const [stats, setStats] = useState<DashboardStats>({
    totalStudents: 0,
    activePrograms: 0,
    sessions: 0,
    successRate: 0,
  })
  const [loading, setLoading] = useState(true)
  const [recentAlerts, setRecentAlerts] = useState<any[]>([])
  const [enrollmentData, setEnrollmentData] = useState<{ name: string; value: number }[]>([])
  const [programDistribution, setProgramDistribution] = useState<ProgramDistributionItem[]>([])
  const [roleData, setRoleData] = useState<RoleSpecificData>({})
  const [systemActivity, setSystemActivity] = useState<any[]>([])
  const [mlModelsPerformance, setMLModelsPerformance] = useState<any[]>([])
  const [availableYears, setAvailableYears] = useState<string[]>([])
  const [selectedYear, setSelectedYear] = useState<string>('')

  // Charger les années académiques disponibles au montage
  useEffect(() => {
    const loadYears = async () => {
      try {
        const sessions = await sessionService.getAll()
        const years = [...new Set(sessions.map(s => s.year).filter(Boolean))].sort().reverse()
        setAvailableYears(years)
        
        // Sélectionner l'année la plus récente par défaut si aucune n'est sélectionnée
        if (years.length > 0 && !selectedYear) {
          setSelectedYear(years[0])
        }
      } catch (error) {
        console.error('Erreur lors du chargement des années:', error)
      }
    }
    loadYears()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const loadData = async () => {
      // Attendre que les années soient chargées avant de charger les données
      if (availableYears.length === 0) return
      
      setLoading(true)
      try {
        // Charger les sessions pour filtrer
        const sessions = await sessionService.getAll()
        
        // Filtrer les données selon l'année sélectionnée (utiliser la première année si aucune n'est sélectionnée)
        const yearFilter = selectedYear || availableYears[0] || null
        const [students, programs, alerts, dashboardStats] = await Promise.all([
          studentService.getAll(),
          programService.getAll(),
          alertService.getAll(),
          analyticsService.getDashboardStats(),
        ])

        // Filtrer les étudiants par session si une année est sélectionnée
        let filteredStudents = students
        if (yearFilter) {
          const sessionsForYear = sessions.filter(s => s.year === yearFilter)
          const sessionIds = sessionsForYear.map(s => s.id)
          filteredStudents = students.filter((s: any) => 
            s.session && sessionIds.includes(s.session)
          )
        }

        // Utiliser les stats réelles du backend, filtrées par année si nécessaire
        const sessionsForYear = yearFilter ? sessions.filter(s => s.year === yearFilter) : sessions
        setStats({
          totalStudents: yearFilter ? filteredStudents.length : (dashboardStats.totalStudents || students.length),
          activePrograms: dashboardStats.activePrograms || programs.filter((p) => p.status === 'active').length,
          sessions: sessionsForYear.length,
          successRate: dashboardStats.successRate || 0,
        })

        setRecentAlerts(alerts.slice(0, 3))

        // Charger données évolution inscriptions depuis API
        if (dashboardStats.enrollmentEvolution && dashboardStats.enrollmentEvolution.length > 0) {
          setEnrollmentData(dashboardStats.enrollmentEvolution.map((e: EnrollmentEvolution) => ({
            name: e.year.toString(),
            value: e.count
          })))
        } else {
          // Fallback: générer depuis les étudiants groupés par année
          const yearCounts: Record<number, number> = {}
          filteredStudents.forEach((s: any) => {
            const year = new Date(s.enrollment_date || s.created_at).getFullYear()
            yearCounts[year] = (yearCounts[year] || 0) + 1
          })
          setEnrollmentData(
            Object.entries(yearCounts)
              .sort(([a], [b]) => Number(a) - Number(b))
              .map(([year, count]) => ({ name: year, value: count }))
          )
        }

        // Distribution par programme depuis API ou calcul
        if (dashboardStats.programDistribution && dashboardStats.programDistribution.length > 0) {
          setProgramDistribution(dashboardStats.programDistribution)
        } else {
          // Fallback: calculer depuis les étudiants filtrés
          const progCounts: Record<string, number> = {}
          filteredStudents.forEach((s: any) => {
            const progName = s.program_name || s.program?.name || 'Autre'
            progCounts[progName] = (progCounts[progName] || 0) + 1
          })
          setProgramDistribution(
            Object.entries(progCounts).map(([name, value]) => ({ name, value }))
          )
        }

        // Charger données spécifiques au rôle
        await loadRoleSpecificData(userRole, alerts, filteredStudents)
        
        // Charger activité système et modèles ML
        if (userRole === 'admin') {
          const activity = await analyticsService.getSystemActivity(10)
          setSystemActivity(activity)
        }
        
        if (userRole === 'ds') {
          const models = await analyticsService.getMLModelsPerformance()
          setMLModelsPerformance(models)
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }

    // Fonction pour charger les données spécifiques au rôle
    const loadRoleSpecificData = async (role: string, alerts: any[], students: any[]) => {
      try {
        switch (role) {
          case 'admin':
            // Admin: données utilisateurs et système
            const usersResponse = await userService.getAll()
            const usersList = Array.isArray(usersResponse) ? usersResponse : (usersResponse.results || [])
            setRoleData({
              totalUsers: usersList.length,
              systemHealth: 'Opérationnel',
            })
            break

          case 'ds':
            // Data Scientist: modèles ML et prédictions
            const [models, predictions] = await Promise.all([
              mlService.getAll(),
              predictionService.getAll(),
            ])
            const highRisk = students.filter((s: any) => s.risk_level === 'high').length
            const activeModel = models.find((m: any) => m.is_active)
            setRoleData({
              activeModels: models.filter((m: any) => m.is_active).length,
              totalPredictions: predictions.length,
              highRiskStudents: highRisk,
              // NO FAKE DEFAULT - null if no model, frontend displays "N/A"
              modelAccuracy: activeModel?.accuracy ? (activeModel.accuracy * 100) : null,
              hasActiveModel: !!activeModel,
            })
            break

          case 'pedagogical':
            // Direction Pédagogique: alertes et interventions
            const openAlerts = alerts.filter((a: any) => a.status === 'new' || a.status === 'acknowledged').length
            const atRisk = students.filter((s: any) => s.risk_level === 'high' || s.risk_level === 'medium').length
            setRoleData({
              openAlerts,
              pendingInterventions: openAlerts, // Approximation
              atRiskStudents: atRisk,
            })
            break

          case 'teacher':
          default:
            // Enseignant: ses étudiants et cours (données filtrées par l'API selon les permissions)
            // L'API filtre automatiquement les étudiants assignés à l'enseignant
            const gradeService = await import('@/api/services/gradeService').then(m => m.gradeService)
            const grades = await gradeService.getAll()
            // Notes sans valeur = notes en attente
            const pendingGrades = Array.isArray(grades) ? grades.filter((g: any) => !g.value && g.value !== 0).length : 0
            setRoleData({
              myStudentsCount: students.length, // L'API filtre déjà par enseignant
              myCoursesCount: new Set(students.map((s: any) => s.program)).size || 1,
              pendingGrades: pendingGrades,
            })
            break
        }
      } catch (error) {
        console.error('Erreur chargement données spécifiques:', error)
      }
    }

    loadData()
  }, [selectedYear, availableYears])

  const handleExportPDF = () => {
    const kpis = [
      { label: 'Total Étudiants', value: stats.totalStudents.toLocaleString() },
      { label: 'Filières Actives', value: stats.activePrograms.toString() },
      { label: 'Sessions', value: stats.sessions.toString() },
      { label: 'Taux de Réussite', value: `${stats.successRate.toFixed(1)}%` },
    ]

    const enrollmentColumns: ExportColumn[] = [
      { key: 'name', label: 'Année' },
      { key: 'value', label: 'Nombre d\'étudiants' },
    ]

    const programColumns: ExportColumn[] = [
      { key: 'name', label: 'Filière' },
      { key: 'value', label: 'Nombre d\'étudiants' },
    ]

    exportDashboardToPDF(
      {
        title: 'Rapport Dashboard Général',
        kpis,
        tables: [
          {
            title: 'Évolution des Inscriptions',
            data: enrollmentData,
            columns: enrollmentColumns,
          },
          {
            title: 'Distribution par Filière',
            data: programDistribution,
            columns: programColumns,
          },
        ],
        charts: [
          {
            title: 'Évolution des Inscriptions',
            description: 'Tendance d\'inscription année par année',
          },
          {
            title: 'Distribution par Filière',
            description: 'Répartition des étudiants par programme',
          },
        ],
      },
      `dashboard-general-${new Date().toISOString().split('T')[0]}`
    )
  }

  // Titres et descriptions personnalisés par rôle
  const getRoleTitle = () => {
    switch (userRole) {
      case 'admin':
        return 'Dashboard Administrateur'
      case 'ds':
        return 'Dashboard Data Science'
      case 'pedagogical':
        return 'Dashboard Pédagogique'
      case 'teacher':
      default:
        return 'Dashboard Enseignant'
    }
  }

  const getRoleDescription = () => {
    switch (userRole) {
      case 'admin':
        return 'Gestion complète du système et des utilisateurs.'
      case 'ds':
        return 'Analyse prédictive et modèles de Machine Learning.'
      case 'pedagogical':
        return 'Suivi des alertes et interventions pédagogiques.'
      case 'teacher':
      default:
        return 'Suivi de vos étudiants et de vos cours.'
    }
  }

  if (loading) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500 dark:text-gray-400">Chargement...</div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  return (
    <MiseEnPagePrincipale title={getRoleTitle()}>
      <div className="mx-auto max-w-7xl flex flex-col gap-8">
        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
              {getRoleTitle()}
            </h1>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              {getRoleDescription()}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <select 
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="appearance-none rounded-lg border border-gray-200 bg-white dark:bg-surface-dark py-2.5 pl-4 pr-10 text-sm font-medium text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700"
              >
                {availableYears.length > 0 ? (
                  availableYears.map((year) => (
                    <option key={year} value={year}>
                      Année académique: {year}
                    </option>
                  ))
                ) : (
                  <option value="">Chargement...</option>
                )}
              </select>
              <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 material-symbols-outlined text-[20px]">
                keyboard_arrow_down
              </span>
            </div>
            <button
              onClick={handleExportPDF}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-hover shadow-sm hover:shadow-md"
            >
              <span className="material-symbols-outlined text-[20px]">download</span>
              <span>Rapport</span>
            </button>
          </div>
        </div>

        {/* KPI Cartes - Personnalisées par rôle */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {/* KPIs pour Admin */}
          {userRole === 'admin' && (
            <>
              <Carte title="Total Utilisateurs" icon="group" iconColor="primary" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {roleData.totalUsers || 0}
                  </p>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">actifs</span>
                </div>
              </Carte>
              <Carte title="Total Étudiants" icon="school" iconColor="blue" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {stats.totalStudents.toLocaleString()}
                  </p>
                  {/* Trend removed - was hardcoded. Real trend requires historical data comparison */}
                </div>
              </Carte>
              <Carte title="Filières Actives" icon="category" iconColor="purple" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.activePrograms}</p>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">programmes</span>
                </div>
              </Carte>
              <Carte title="État Système" icon="dns" iconColor="green" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-lg font-bold text-green-600">{roleData.systemHealth || 'OK'}</p>
                  <Badge variant="success" size="sm">En ligne</Badge>
                </div>
              </Carte>
            </>
          )}

          {/* KPIs pour Data Scientist */}
          {userRole === 'ds' && (
            <>
              <Carte title="Modèles Actifs" icon="psychology" iconColor="purple" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {roleData.activeModels || 1}
                  </p>
                  <span className="text-xs font-medium text-green-600">déployé(s)</span>
                </div>
              </Carte>
              <Carte title="Prédictions" icon="analytics" iconColor="blue" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {roleData.totalPredictions || 0}
                  </p>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">générées</span>
                </div>
              </Carte>
              <Carte title="Étudiants à Risque" icon="warning" iconColor="red" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-red-600">{roleData.highRiskStudents || 0}</p>
                  <span className="text-xs font-medium text-red-600">risque élevé</span>
                </div>
              </Carte>
              <Carte title="Précision Modèle" icon="speed" iconColor={roleData.hasActiveModel ? "green" : "gray"} hover>
                <div className="mt-4 flex items-baseline gap-2">
                  {roleData.modelAccuracy != null ? (
                    <p className="text-3xl font-bold text-green-600">
                      {roleData.modelAccuracy.toFixed(1)}%
                    </p>
                  ) : (
                    <p className="text-2xl font-bold text-gray-400">
                      N/A
                    </p>
                  )}
                  {roleData.hasActiveModel === false && (
                    <span className="text-xs font-medium text-amber-600">Aucun modèle</span>
                  )}
                </div>
              </Carte>
            </>
          )}

          {/* KPIs pour Direction Pédagogique */}
          {userRole === 'pedagogical' && (
            <>
              <Carte title="Alertes Ouvertes" icon="notification_important" iconColor="red" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-red-600">{roleData.openAlerts || 0}</p>
                  <span className="text-xs font-medium text-red-600">à traiter</span>
                </div>
              </Carte>
              <Carte title="Étudiants à Risque" icon="person_alert" iconColor="orange" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-orange-600">{roleData.atRiskStudents || 0}</p>
                  <span className="text-xs font-medium text-orange-600">nécessitent suivi</span>
                </div>
              </Carte>
              <Carte title="Interventions" icon="support_agent" iconColor="blue" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {roleData.pendingInterventions || 0}
                  </p>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">en cours</span>
                </div>
              </Carte>
              <Carte title="Taux de Réussite" icon="emoji_events" iconColor="green" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-green-600">{stats.successRate}%</p>
                  {/* Trend removed - was hardcoded fake value */}
                </div>
              </Carte>
            </>
          )}

          {/* KPIs pour Enseignant */}
          {userRole === 'teacher' && (
            <>
              <Carte title="Mes Étudiants" icon="groups" iconColor="primary" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {roleData.myStudentsCount || 0}
                  </p>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">suivis</span>
                </div>
              </Carte>
              <Carte title="Mes Cours" icon="class" iconColor="purple" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {roleData.myCoursesCount || 0}
                  </p>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">cette session</span>
                </div>
              </Carte>
              <Carte title="Notes en Attente" icon="edit_note" iconColor="orange" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-orange-600">{roleData.pendingGrades || 0}</p>
                  <span className="text-xs font-medium text-orange-600">à saisir</span>
                </div>
              </Carte>
              <Carte title="Taux de Réussite" icon="trending_up" iconColor="green" hover>
                <div className="mt-4 flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-green-600">{stats.successRate}%</p>
                  {/* Trend removed - was hardcoded fake value */}
                </div>
              </Carte>
            </>
          )}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Line Chart */}
          <Carte className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                  Évolution des Inscriptions
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Tendances de croissance année par année
                </p>
              </div>
            </div>
            <GraphiqueLignes
              data={enrollmentData}
              dataKey="name"
              lines={[
                { key: 'value', name: 'Inscriptions', color: '#1c41a6' },
              ]}
              height={300}
            />
          </Carte>

          {/* Pie Chart */}
          <Carte>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
              Répartition par Filière
            </h2>
            <GraphiqueCirculaire data={programDistribution} height={300} />
          </Carte>
        </div>

        {/* Bottom Section: Contenu spécifique au rôle */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Section principale - varie selon le rôle */}
          <div className="lg:col-span-2 rounded-xl border border-gray-200 bg-white dark:bg-surface-dark shadow-sm overflow-hidden">
            {/* Admin: Sessions et Utilisateurs */}
            {userRole === 'admin' && (
              <>
                <div className="border-b border-gray-100 dark:border-gray-800 p-6 flex justify-between items-center">
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                    Activité Récente du Système
                  </h2>
                  <Link to="/utilisateurs" className="text-sm font-medium text-primary hover:text-primary-hover">
                    Gérer les utilisateurs
                  </Link>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-xs uppercase text-gray-600 dark:bg-gray-800/50 dark:text-gray-400">
                      <tr>
                        <th className="px-6 py-4 font-semibold">Action</th>
                        <th className="px-6 py-4 font-semibold">Utilisateur</th>
                        <th className="px-6 py-4 font-semibold">Date</th>
                        <th className="px-6 py-4 font-semibold">Statut</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                      {systemActivity.length > 0 ? (
                        systemActivity.map((activity) => (
                          <tr key={activity.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{activity.action}</td>
                            <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{activity.user}</td>
                            <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{activity.time}</td>
                            <td className="px-6 py-4">
                              <Badge variant={activity.status === 'success' ? 'success' : activity.status === 'error' ? 'danger' : 'info'}>
                                {activity.status === 'success' ? 'Réussie' : activity.status === 'error' ? 'Erreur' : 'Info'}
                              </Badge>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                            Aucune activité récente
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* Data Scientist: Modèles et Prédictions */}
            {userRole === 'ds' && (
              <>
                <div className="border-b border-gray-100 dark:border-gray-800 p-6 flex justify-between items-center">
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                    Performance des Modèles ML
                  </h2>
                  <Link to="/module-ia/modeles" className="text-sm font-medium text-primary hover:text-primary-hover">
                    Voir les modèles
                  </Link>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-xs uppercase text-gray-600 dark:bg-gray-800/50 dark:text-gray-400">
                      <tr>
                        <th className="px-6 py-4 font-semibold">Modèle</th>
                        <th className="px-6 py-4 font-semibold">Type</th>
                        <th className="px-6 py-4 font-semibold">Précision</th>
                        <th className="px-6 py-4 font-semibold">Statut</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                      {mlModelsPerformance.length > 0 ? (
                        mlModelsPerformance.map((model, index) => (
                          <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{model.name}</td>
                            <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{model.type}</td>
                            <td className={`px-6 py-4 font-semibold ${model.accuracy >= 90 ? 'text-green-600' : model.accuracy >= 80 ? 'text-yellow-600' : 'text-gray-600'}`}>
                              {model.accuracy}%
                            </td>
                            <td className="px-6 py-4">
                              <Badge variant={model.statusCode === 'active' ? 'success' : model.statusCode === 'archived' ? 'info' : model.statusCode === 'training' ? 'warning' : 'danger'}>
                                {model.status}
                              </Badge>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                            Aucun modèle ML disponible
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* Direction Pédagogique: Alertes et Interventions */}
            {userRole === 'pedagogical' && (
              <>
                <div className="border-b border-gray-100 dark:border-gray-800 p-6 flex justify-between items-center">
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                    Alertes Prioritaires
                  </h2>
                  <Link to="/alertes" className="text-sm font-medium text-primary hover:text-primary-hover">
                    Voir toutes les alertes
                  </Link>
                </div>
                <div className="p-6 space-y-4">
                  {recentAlerts.length > 0 ? recentAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={clsx(
                        'flex gap-4 p-4 rounded-lg border',
                        alert.level === 'high' || alert.level === 'critical'
                          ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
                          : 'bg-orange-50 border-orange-200 dark:bg-orange-900/20 dark:border-orange-800'
                      )}
                    >
                      <div className="shrink-0">
                        <span className={clsx(
                          'material-symbols-outlined text-2xl',
                          alert.level === 'high' || alert.level === 'critical' ? 'text-red-600' : 'text-orange-600'
                        )}>
                          warning
                        </span>
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 dark:text-white">{alert.message}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {alert.studentName} - {alert.programName}
                        </p>
                      </div>
                      <Link 
                        to={`/alertes/${alert.id}`}
                        className="text-primary hover:text-primary-hover font-medium text-sm"
                      >
                        Intervenir
                      </Link>
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-8">Aucune alerte prioritaire</p>
                  )}
                </div>
              </>
            )}

            {/* Enseignant: Accès rapide */}
            {userRole === 'teacher' && (
              <>
                <div className="border-b border-gray-100 dark:border-gray-800 p-6 flex justify-between items-center">
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                    Accès Rapide
                  </h2>
                  <Link to="/gestion/notes" className="text-sm font-medium text-primary hover:text-primary-hover">
                    Saisir des notes
                  </Link>
                </div>
                <div className="p-6 space-y-4">
                  <Link 
                    to="/students" 
                    className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">groups</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">Mes Étudiants</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{roleData.myStudentsCount || 0} étudiants assignés</p>
                    </div>
                    <span className="ml-auto material-symbols-outlined text-gray-400">chevron_right</span>
                  </Link>
                  <Link 
                    to="/gestion/notes" 
                    className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                      <span className="material-symbols-outlined text-green-600 dark:text-green-400">grade</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">Saisie des Notes</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {roleData.pendingGrades && roleData.pendingGrades > 0 
                          ? `${roleData.pendingGrades} notes en attente`
                          : 'Notes à jour'}
                      </p>
                    </div>
                    <span className="ml-auto material-symbols-outlined text-gray-400">chevron_right</span>
                  </Link>
                  <Link 
                    to="/gestion/absences" 
                    className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                      <span className="material-symbols-outlined text-orange-600 dark:text-orange-400">event_busy</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">Gestion des Absences</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Suivre les présences</p>
                    </div>
                    <span className="ml-auto material-symbols-outlined text-gray-400">chevron_right</span>
                  </Link>
                </div>
              </>
            )}
          </div>

          {/* Widget latéral - Insights IA (commun mais adapté) */}
          <div className="rounded-xl border border-indigo-100 dark:border-indigo-900/50 bg-white dark:bg-surface-dark shadow-sm flex flex-col h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-8 -mr-8 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>
            <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center relative z-10">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-purple-600 dark:text-purple-400">
                  {userRole === 'ds' ? 'psychology' : userRole === 'pedagogical' ? 'support_agent' : 'auto_awesome'}
                </span>
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                  {userRole === 'ds' ? 'Dernières Prédictions' : userRole === 'pedagogical' ? 'Actions Rapides' : 'Insights IA'}
                </h2>
              </div>
              <Badge variant="primary" size="sm">
                {userRole === 'ds' ? 'ML' : 'Live'}
              </Badge>
            </div>
            <div className="p-6 flex flex-col gap-4 relative z-10">
              {userRole === 'pedagogical' ? (
                // Actions rapides pour Direction Pédagogique
                <>
                  <Link to="/gestion/etudiants" className="flex items-center gap-3 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                    <span className="material-symbols-outlined text-blue-600">person_search</span>
                    <span className="font-medium text-blue-900 dark:text-blue-200">Voir étudiants à risque</span>
                  </Link>
                  <Link to="/alertes" className="flex items-center gap-3 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors">
                    <span className="material-symbols-outlined text-red-600">notification_important</span>
                    <span className="font-medium text-red-900 dark:text-red-200">Traiter les alertes</span>
                  </Link>
                  <Link to="/analytics" className="flex items-center gap-3 p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
                    <span className="material-symbols-outlined text-purple-600">insights</span>
                    <span className="font-medium text-purple-900 dark:text-purple-200">Voir les analytics</span>
                  </Link>
                </>
              ) : userRole === 'teacher' ? (
                // Actions pour Enseignant
                <>
                  <Link to="/gestion/notes" className="flex items-center gap-3 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                    <span className="material-symbols-outlined text-blue-600">edit_note</span>
                    <span className="font-medium text-blue-900 dark:text-blue-200">Saisir des notes</span>
                  </Link>
                  <Link to="/gestion/absences" className="flex items-center gap-3 p-4 rounded-lg bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors">
                    <span className="material-symbols-outlined text-orange-600">event_busy</span>
                    <span className="font-medium text-orange-900 dark:text-orange-200">Gérer les absences</span>
                  </Link>
                  <Link to="/gestion/etudiants" className="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
                    <span className="material-symbols-outlined text-green-600">groups</span>
                    <span className="font-medium text-green-900 dark:text-green-200">Mes étudiants</span>
                  </Link>
                </>
              ) : (
                // Alertes IA par défaut (admin, ds)
                recentAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={clsx(
                      'flex gap-4 p-4 rounded-lg border',
                      alert.level === 'high' || alert.level === 'critical'
                        ? 'bg-red-50 border-red-100 dark:bg-red-900/10 dark:border-red-900/30'
                        : 'bg-blue-50 border-blue-100 dark:bg-blue-900/10 dark:border-blue-900/30'
                    )}
                  >
                    <div className="shrink-0 mt-0.5">
                      <span
                        className={clsx(
                          'material-symbols-outlined text-[20px]',
                          alert.level === 'high' || alert.level === 'critical'
                            ? 'text-red-600 dark:text-red-400'
                            : 'text-blue-600 dark:text-blue-400'
                        )}
                      >
                        {alert.level === 'high' || alert.level === 'critical'
                          ? 'warning'
                          : 'info'}
                      </span>
                    </div>
                    <div>
                      <h3
                        className={clsx(
                          'text-sm font-semibold',
                          alert.level === 'high' || alert.level === 'critical'
                            ? 'text-red-900 dark:text-red-200'
                            : 'text-blue-900 dark:text-blue-200'
                        )}
                      >
                        {alert.message}
                      </h3>
                      <p
                        className={clsx(
                          'text-xs mt-1',
                          alert.level === 'high' || alert.level === 'critical'
                            ? 'text-red-700 dark:text-red-300'
                            : 'text-blue-700 dark:text-blue-300'
                        )}
                      >
                        {alert.studentName} - {alert.programName}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </MiseEnPagePrincipale>
  )
}

