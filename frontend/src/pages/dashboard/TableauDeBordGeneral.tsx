import { useEffect, useState } from 'react'
import { clsx } from 'clsx'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Badge from '@/components/common/Badge'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import GraphiqueCirculaire from '@/components/charts/GraphiqueCirculaire'
import { studentService } from '@/api/services/studentService'
import { programService } from '@/api/services/programService'
import { sessionService } from '@/api/services/sessionService'
import { alertService } from '@/api/services/alertService'
import { exportDashboardToPDF, type ExportColumn } from '@/utils/exportService'

interface DashboardStats {
  totalStudents: number
  activePrograms: number
  sessions: number
  successRate: number
}

export default function TableauDeBordGeneral() {
  const [stats, setStats] = useState<DashboardStats>({
    totalStudents: 0,
    activePrograms: 0,
    sessions: 0,
    successRate: 0,
  })
  const [loading, setLoading] = useState(true)
  const [recentAlerts, setRecentAlerts] = useState<any[]>([])

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const [students, programs, sessions, alerts] = await Promise.all([
          studentService.getAll(),
          programService.getAll(),
          sessionService.getAll(),
          alertService.getAll(),
        ])

        setStats({
          totalStudents: students.length * 100, // Simuler plus d'étudiants
          activePrograms: programs.filter((p) => p.status === 'active').length,
          sessions: sessions.length * 10, // Simuler plus de sessions
          successRate: 88.2,
        })

        setRecentAlerts(alerts.slice(0, 3))
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  // Données pour les graphiques
  const enrollmentData = [
    { name: '2019', value: 1800 },
    { name: '2020', value: 1950 },
    { name: '2021', value: 2100 },
    { name: '2022', value: 2300 },
    { name: '2023', value: 2450 },
    { name: '2024', value: 2650 },
  ]

  const programDistribution = [
    { name: 'Informatique', value: 850 },
    { name: 'Génie Logiciel', value: 650 },
    { name: 'Réseaux', value: 450 },
    { name: 'Cybersécurité', value: 300 },
  ]

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
    <MiseEnPagePrincipale title="Dashboard Général">
      <div className="mx-auto max-w-7xl flex flex-col gap-8">
        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
              Dashboard Général
            </h1>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              Vue d'ensemble des performances académiques et des insights.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <select className="appearance-none rounded-lg border border-gray-200 bg-white dark:bg-surface-dark py-2.5 pl-4 pr-10 text-sm font-medium text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700">
                <option>Année académique: 2023-2024</option>
                <option>Année académique: 2022-2023</option>
                <option>Année académique: 2021-2022</option>
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

        {/* KPI Cartes */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <Carte
            title="Total Étudiants"
            icon="groups"
            iconColor="primary"
            hover
          >
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.totalStudents.toLocaleString()}
              </p>
              <span className="flex items-center text-xs font-medium text-green-600">
                <span className="material-symbols-outlined text-[14px]">
                  trending_up
                </span>
                5%
              </span>
            </div>
          </Carte>

          <Carte
            title="Filières Actives"
            icon="school"
            iconColor="purple"
            hover
          >
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.activePrograms}
              </p>
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                Stable
              </span>
            </div>
          </Carte>

          <Carte title="Sessions" icon="event_note" iconColor="orange" hover>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.sessions}
              </p>
              <span className="flex items-center text-xs font-medium text-green-600">
                <span className="material-symbols-outlined text-[14px]">
                  trending_up
                </span>
                12%
              </span>
            </div>
          </Carte>

          <Carte
            title="Taux de Réussite"
            icon="auto_graph"
            iconColor="green"
            hover
          >
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.successRate}%
              </p>
              <span className="flex items-center text-xs font-medium text-green-600">
                <span className="material-symbols-outlined text-[14px]">
                  arrow_upward
                </span>
                2%
              </span>
            </div>
          </Carte>
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

        {/* Bottom Section: Recent Sessions & AI Alerts */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Recent Sessions Table */}
          <div className="lg:col-span-2 rounded-xl border border-gray-200 bg-white dark:bg-surface-dark shadow-sm overflow-hidden">
            <div className="border-b border-gray-100 dark:border-gray-800 p-6 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                Sessions Récentes
              </h2>
              <button className="text-sm font-medium text-primary hover:text-primary-hover">
                Voir tout
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-600 dark:bg-gray-800/50 dark:text-gray-400">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Nom Session</th>
                    <th className="px-6 py-4 font-semibold">Date & Heure</th>
                    <th className="px-6 py-4 font-semibold">Filière</th>
                    <th className="px-6 py-4 font-semibold">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                      Data Mining Avancé
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      24 Oct, 09:00
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      Informatique
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="success">Terminé</Badge>
                    </td>
                  </tr>
                  <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                      Programmation Web
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      24 Oct, 11:30
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      Génie Logiciel
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="info">En cours</Badge>
                    </td>
                  </tr>
                  <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                      Sécurité Réseaux
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      25 Oct, 09:00
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      Cybersécurité
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="warning">Planifié</Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* AI Alerts Widget */}
          <div className="rounded-xl border border-indigo-100 dark:border-indigo-900/50 bg-white dark:bg-surface-dark shadow-sm flex flex-col h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-8 -mr-8 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>
            <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center relative z-10">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-purple-600 dark:text-purple-400">
                  auto_awesome
                </span>
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                  Insights IA
                </h2>
              </div>
              <Badge variant="primary" size="sm">
                Live
              </Badge>
            </div>
            <div className="p-6 flex flex-col gap-4 relative z-10">
              {recentAlerts.map((alert) => (
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
              ))}
            </div>
          </div>
        </div>
      </div>
    </MiseEnPagePrincipale>
  )
}

