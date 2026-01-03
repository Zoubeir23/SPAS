import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import GraphiqueBarres from '@/components/charts/GraphiqueBarres'
import { exportToExcel, exportDashboardToPDF, type ExportColumn } from '@/utils/exportService'
import { analyticsService, type AnalyticsMetrics, type DropoutEvolution, type ProgramPerformance, type InterventionEfficacy, type RiskDistribution } from '@/api/services/analyticsService'

export default function AnalysesAvancees() {
  const [startDate, setStartDate] = useState('2023-09-01')
  const [endDate, setEndDate] = useState('2024-06-30')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Données depuis l'API
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null)
  const [dropoutData, setDropoutData] = useState<DropoutEvolution[]>([])
  const [performanceByProgram, setPerformanceByProgram] = useState<ProgramPerformance[]>([])
  const [interventionEfficacy, setInterventionEfficacy] = useState<InterventionEfficacy[]>([])
  const [riskDistribution, setRiskDistribution] = useState<RiskDistribution[]>([])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [metricsData, riskData] = await Promise.all([
        analyticsService.getMetrics(startDate, endDate),
        analyticsService.getRiskDistribution()
      ])
      setMetrics(metricsData)
      setDropoutData(metricsData.dropoutEvolution)
      setPerformanceByProgram(metricsData.performanceByProgram)
      setInterventionEfficacy(metricsData.interventionEfficacy)
      setRiskDistribution(riskData)
    } catch (err) {
      console.error('Erreur lors du chargement des analytics:', err)
      setError('Impossible de charger les données analytiques')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleApplyFilters = () => {
    loadData()
  }

  const handleExportPDF = () => {
    const kpis = [
      { label: 'Risque de Décrochage Global', value: metrics?.riskGlobal ? `${metrics.riskGlobal}%` : '0%' },
      { label: 'Interventions Actives', value: metrics?.interventionsActives?.toString() ?? '0' },
      { label: 'Précision Modèle IA', value: metrics?.precisionModele ? `${metrics.precisionModele}%` : '0%' },
    ]

    const interventionColumns: ExportColumn[] = [
      { key: 'type', label: 'Type d\'Intervention' },
      { key: 'students', label: 'Nombre d\'Étudiants' },
      { key: 'gpaImpact', label: 'Impact Moyen (GPA)' },
      { key: 'retention', label: 'Rétention' },
      { key: 'efficacy', label: 'Efficacité' },
    ]

    const dropoutColumns: ExportColumn[] = [
      { key: 'month', label: 'Mois' },
      { key: 'predicted', label: 'Prédit (IA)', format: (v) => `${v}%` },
      { key: 'real', label: 'Réel', format: (v) => `${v}%` },
    ]

    exportDashboardToPDF(
      {
        title: 'Rapport Analytics Avancées',
        kpis,
        tables: [
          {
            title: 'Efficacité des Interventions',
            data: interventionEfficacy,
            columns: interventionColumns,
          },
          {
            title: 'Taux de Décrochage Prédit vs Réel',
            data: dropoutData,
            columns: dropoutColumns,
          },
        ],
        charts: [
          {
            title: 'Taux de Décrochage Prédit vs Réel',
            description: 'Comparaison sur l\'année académique en cours',
          },
          {
            title: 'Performance par Filière',
            description: 'Répartition des taux de réussite, risque et décrochage',
          },
        ],
      },
      `analytics-avancees-${new Date().toISOString().split('T')[0]}`
    )
  }

  const handleExportExcel = () => {
    const interventionColumns: ExportColumn[] = [
      { key: 'type', label: 'Type d\'Intervention' },
      { key: 'students', label: 'Nombre d\'Étudiants' },
      { key: 'gpaImpact', label: 'Impact Moyen (GPA)' },
      { key: 'retention', label: 'Rétention' },
      { key: 'efficacy', label: 'Efficacité' },
    ]

    exportToExcel(
      interventionEfficacy,
      interventionColumns,
      `rapport-analytics-${new Date().toISOString().split('T')[0]}`,
      'Efficacité Interventions'
    )
  }

  return (
    <MiseEnPagePrincipale title="Analytics Avancées">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Breadcrumbs */}
        <nav className="mb-4 flex items-center text-sm font-medium text-gray-600 dark:text-gray-400">
          <button className="hover:text-primary transition-colors">Accueil</button>
          <span className="mx-2 text-gray-400">/</span>
          <span className="text-primary font-semibold">Analytics Avancées</span>
        </nav>

        {/* Page Heading & Date Filters */}
        <div className="mb-8 flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-gray-900 dark:text-white">
              Analytics Avancées
            </h1>
            <p className="text-base text-gray-600 dark:text-gray-400">
              Suivi des performances académiques et prédictions IA en temps réel.
            </p>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
                Période du
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
                  calendar_today
                </span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="h-10 w-40 rounded-lg border border-gray-200 bg-white px-3 pl-10 text-sm font-medium text-gray-900 focus:border-primary focus:ring-1 focus:ring-primary dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">au</label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
                  event
                </span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="h-10 w-40 rounded-lg border border-gray-200 bg-white px-3 pl-10 text-sm font-medium text-gray-900 focus:border-primary focus:ring-1 focus:ring-primary dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>
            <Bouton onClick={handleApplyFilters} disabled={loading} className="mb-[1px]">
              <span className="material-symbols-outlined text-lg">filter_list</span>
              {loading ? 'Chargement...' : 'Appliquer'}
            </Bouton>
          </div>
        </div>

        {/* Erreur */}
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800">
            <span className="material-symbols-outlined mr-2 align-middle">error</span>
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">Chargement des données...</span>
          </div>
        )}

        {/* KPI Cartes Row */}
        {!loading && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {/* KPI 1 */}
          <Carte>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Risque de Décrochage Global
              </h3>
              <span className="rounded-full bg-red-100 p-1.5 text-red-600 dark:bg-red-900/30 dark:text-red-400">
                <span className="material-symbols-outlined text-sm font-bold">trending_up</span>
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{metrics?.riskGlobal?.toFixed(1) ?? '0'}%</p>
              <span className="text-sm font-medium text-gray-500">calculé</span>
            </div>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-500">basé sur les prédictions actives</p>
          </Carte>

          {/* KPI 2 */}
          <Carte>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Interventions Actives
              </h3>
              <span className="rounded-full bg-primary/20 p-1.5 text-primary">
                <span className="material-symbols-outlined text-sm font-bold">psychology</span>
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{metrics?.interventionsActives ?? 0}</p>
              <span className="text-sm font-medium text-green-600">en cours</span>
            </div>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-500">interventions pédagogiques</p>
          </Carte>

          {/* KPI 3 */}
          <Carte>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Précision Modèle IA
              </h3>
              <span className="rounded-full bg-green-100 p-1.5 text-green-600 dark:bg-green-900/30 dark:text-green-400">
                <span className="material-symbols-outlined text-sm font-bold">auto_awesome</span>
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{metrics?.precisionModele?.toFixed(1) ?? '0'}%</p>
              <span className="text-sm font-medium text-green-600">Score F1</span>
            </div>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-500">modèle ML actif</p>
          </Carte>
        </div>
        )}

        {/* Main Chart: Dropout Rate */}
        {!loading && (
        <>
        <Carte className="lg:col-span-8">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                Taux de Décrochage Prédit vs Réel
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Comparaison sur l'année académique en cours
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-primary"></span>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Prédit (IA)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-green-600"></span>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Réel</span>
              </div>
            </div>
          </div>
          {dropoutData.length > 0 ? (
            <GraphiqueLignes
              data={dropoutData}
              dataKey="month"
              lines={[
                { key: 'predicted', name: 'Prédit (IA)', color: '#7c3bed' },
                { key: 'real', name: 'Réel', color: '#16A34A' },
              ]}
              height={300}
            />
          ) : (
            <p className="text-center text-gray-500 py-8">Aucune donnée d'évolution disponible</p>
          )}
        </Carte>

        {/* Performance by Program */}
        <Carte>
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Performance par Filière
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Répartition des taux de réussite, risque et décrochage
            </p>
          </div>
          {performanceByProgram.length > 0 ? (
            <GraphiqueBarres
              data={performanceByProgram}
              bars={[
                { key: 'success', name: 'Réussite', color: '#16A34A' },
                { key: 'risk', name: 'À risque', color: '#F59E0B' },
                { key: 'dropout', name: 'Décrochage', color: '#DC2626' },
              ]}
              xAxisKey="program"
              height={300}
            />
          ) : (
            <p className="text-center text-gray-500 py-8">Aucune donnée de performance par filière disponible</p>
          )}
        </Carte>
        </>
        )}

        {/* Additional Analytics Grid */}
        {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Distribution */}
          <Carte>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Distribution des Risques
            </h3>
            <div className="space-y-4">
              {riskDistribution.length > 0 ? (
                riskDistribution.map((risk) => {
                  const colorMap: Record<string, string> = {
                    'low': 'bg-green-500',
                    'medium': 'bg-amber-500',
                    'high': 'bg-red-500',
                    'critical': 'bg-red-700'
                  }
                  const labelMap: Record<string, string> = {
                    'low': 'Faible',
                    'medium': 'Moyen',
                    'high': 'Élevé',
                    'critical': 'Critique'
                  }
                  return (
                    <div key={risk.level}>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600 dark:text-gray-400">{labelMap[risk.level] || risk.level}</span>
                        <span className="font-semibold text-gray-900 dark:text-white">{risk.percentage.toFixed(0)}% ({risk.count})</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                        <div className={`${colorMap[risk.level] || 'bg-gray-500'} h-3 rounded-full`} style={{ width: `${risk.percentage}%` }}></div>
                      </div>
                    </div>
                  )
                })
              ) : (
                <p className="text-gray-500 text-sm">Aucune donnée de risque disponible</p>
              )}
            </div>
          </Carte>

          {/* Intervention Effectiveness */}
          <Carte>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Efficacité des Interventions
            </h3>
            <div className="space-y-4">
              {interventionEfficacy.length > 0 ? (
                interventionEfficacy.map((intervention, index) => {
                  const retentionValue = parseInt(intervention.retention.replace(/[^0-9]/g, '')) || 0
                  const colorClass = retentionValue >= 10 ? 'text-green-600' : retentionValue >= 5 ? 'text-amber-600' : 'text-gray-600'
                  return (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white">{intervention.type}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {intervention.students} étudiants • Impact: {intervention.gpaImpact}
                        </p>
                      </div>
                      <span className={`text-2xl font-bold ${colorClass}`}>{intervention.retention}</span>
                    </div>
                  )
                })
              ) : (
                <p className="text-gray-500 text-sm">Aucune intervention enregistrée</p>
              )}
            </div>
          </Carte>
        </div>
        )}

        {/* Export Buttons */}
        <div className="sticky bottom-4 z-20 mt-8 flex flex-wrap justify-end gap-4 rounded-xl border border-gray-200 bg-white/80 p-4 shadow-lg backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80">
          <Bouton
            onClick={handleExportPDF}
            variant="outline"
            className="flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">picture_as_pdf</span>
            Générer PDF
          </Bouton>
          <Bouton
            onClick={handleExportExcel}
            className="flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">table_view</span>
            Exporter Rapport Excel
          </Bouton>
        </div>
      </div>
    </MiseEnPagePrincipale>
  )
}
