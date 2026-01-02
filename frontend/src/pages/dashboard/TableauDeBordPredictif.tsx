import { useEffect, useState } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import GraphiqueJauge from '@/components/charts/GraphiqueJauge'
import GraphiqueBarres from '@/components/charts/GraphiqueBarres'
import { predictionService } from '@/api/services/predictionService'
import { alertService } from '@/api/services/alertService'
import { exportDashboardToPDF, type ExportColumn } from '@/utils/exportService'

export default function TableauDeBordPredictif() {
  const [predictions, setPredictions] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const [preds, alrts] = await Promise.all([
          predictionService.getAll(),
          alertService.getAll(),
        ])
        setPredictions(preds)
        setAlerts(alrts)
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const riskDistribution = [
    { name: 'Faible', value: 65 },
    { name: 'Moyen', value: 25 },
    { name: 'Élevé', value: 8 },
    { name: 'Critique', value: 2 },
  ]

  const handleExportPDF = () => {
    const kpis = [
      { label: 'Taux de Réussite Prédit', value: '87.4%' },
      {
        label: 'Étudiants à Risque',
        value: alerts.filter((a) => a.level === 'high' || a.level === 'critical').length.toString(),
      },
      { label: 'Prédictions Actives', value: predictions.length.toString() },
      { label: 'Modèles ML', value: '2' },
    ]

    const riskColumns: ExportColumn[] = [
      { key: 'name', label: 'Niveau de Risque' },
      { key: 'value', label: 'Pourcentage', format: (v) => `${v}%` },
    ]

    const alertColumns: ExportColumn[] = [
      { key: 'message', label: 'Message' },
      { key: 'studentName', label: 'Étudiant' },
      { key: 'programName', label: 'Programme' },
      {
        key: 'level',
        label: 'Niveau',
        format: (v) => (v === 'high' ? 'Élevé' : v === 'critical' ? 'Critique' : 'Moyen'),
      },
    ]

    exportDashboardToPDF(
      {
        title: 'Rapport Dashboard Prédictif',
        kpis,
        tables: [
          {
            title: 'Distribution des Risques',
            data: riskDistribution,
            columns: riskColumns,
          },
          {
            title: 'Alertes Prédictives Récentes',
            data: alerts.slice(0, 10),
            columns: alertColumns,
          },
        ],
        charts: [
          {
            title: 'Distribution des Risques',
            description: 'Répartition des étudiants par niveau de risque',
          },
          {
            title: 'Score Global',
            description: 'Taux de réussite prédit: 87.4%',
          },
        ],
      },
      `dashboard-predictif-${new Date().toISOString().split('T')[0]}`
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
    <MiseEnPagePrincipale title="Dashboard Prédictif">
      <div className="mx-auto max-w-7xl flex flex-col gap-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
              Dashboard Prédictif
            </h1>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              Vue d'ensemble des prédictions ML et des risques détectés.
            </p>
          </div>
          <Bouton onClick={handleExportPDF} variant="outline" className="flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">picture_as_pdf</span>
            Rapport Complet PDF
          </Bouton>
        </div>

        {/* KPI Cartes */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <Carte title="Taux de Réussite Prédit" icon="analytics" iconColor="primary" hover>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">87.4%</p>
            </div>
          </Carte>
          <Carte title="Étudiants à Risque" icon="warning" iconColor="danger" hover>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {alerts.filter((a) => a.level === 'high' || a.level === 'critical').length}
              </p>
            </div>
          </Carte>
          <Carte title="Prédictions Actives" icon="psychology" iconColor="purple" hover>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {predictions.length}
              </p>
            </div>
          </Carte>
          <Carte title="Modèles ML" icon="model_training" iconColor="orange" hover>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">2</p>
            </div>
          </Carte>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Carte className="lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
              Distribution des Risques
            </h2>
            <GraphiqueBarres
              data={riskDistribution}
              bars={[{ key: 'value', name: 'Nombre d\'étudiants', color: '#1c41a6' }]}
              height={300}
            />
          </Carte>
          <Carte>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
              Score Global
            </h2>
            <GraphiqueJauge value={87.4} label="Taux de réussite prédit" />
          </Carte>
        </div>

        {/* Recent Alerts */}
        <Carte>
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
            Alertes Prédictives Récentes
          </h2>
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex gap-4 p-4 rounded-lg border bg-red-50 border-red-100 dark:bg-red-900/10 dark:border-red-900/30"
              >
                <span className="material-symbols-outlined text-red-600 dark:text-red-400">
                  warning
                </span>
                <div>
                  <h3 className="text-sm font-semibold text-red-900 dark:text-red-200">
                    {alert.message}
                  </h3>
                  <p className="text-xs mt-1 text-red-700 dark:text-red-300">
                    {alert.studentName} - {alert.programName}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Carte>
      </div>
    </MiseEnPagePrincipale>
  )
}

