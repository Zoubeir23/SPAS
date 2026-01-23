import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import Carte from '@/components/common/Carte'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import ModaleEntrainement from '@/components/modals/ModaleEntrainement'
import { mlService, MLModel } from '@/api/services/mlService'
import { analyticsService } from '@/api/services/analyticsService'
import { ROUTES } from '@/utils/constants'
import { exportToExcel, type ExportColumn } from '@/utils/exportService'

// Helper pour normaliser les métriques (si > 1, c'est déjà en %)
const formatMetric = (value: number | string | undefined, decimals: number = 1): string => {
  if (value === undefined || value === null || value === '') return '0'
  // Convertir en nombre (peut être string depuis Django Decimal)
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return '0'
  // Si la valeur est > 1, elle est déjà en pourcentage (0-100 scale)
  const normalized = numValue > 1 ? numValue : numValue * 100
  return normalized.toFixed(decimals)
}

interface TrainingJob {
  id: string
  name: string
  status: 'running' | 'pending' | 'completed' | 'failed'
  progress: number
  algorithm: string
  startedAt: string
}

interface PerformanceDataPoint {
  date: string
  value: number
}

export default function GestionModeles() {
  const navigate = useNavigate()
  const [models, setModels] = useState<MLModel[]>([])
  const [filteredModels, setFilteredModels] = useState<MLModel[]>([])
  const [loading, setLoading] = useState(true)
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([])
  const [performanceData, setPerformanceData] = useState<PerformanceDataPoint[]>([])
  const [showTrainingModal, setShowTrainingModal] = useState(false)
  const [showCompareModal, setShowCompareModal] = useState(false)
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [periodFilter, setPeriodFilter] = useState<'30' | '7' | '24'>('30')

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const [modelsData, performanceHistory] = await Promise.all([
          mlService.getAll(),
          analyticsService.getModelPerformanceHistory()
        ])
        setModels(modelsData)
        setFilteredModels(modelsData)
        
        // Transformer performance history pour le graphique
        if (performanceHistory && performanceHistory.length > 0) {
          setPerformanceData(performanceHistory.map((p: any) => ({
            date: p.date,
            value: Math.round(p.accuracy * 100)
          })))
        } else {
          // Pas de données disponibles - afficher vide
          setPerformanceData([])
        }
        
        // Charger les jobs d'entraînement depuis l'API
        try {
          const jobs = await mlService.getTrainingJobs()
          if (jobs && jobs.length > 0) {
            setTrainingJobs(jobs.map((job: any) => ({
              id: job.id.toString(),
              name: `Job #${job.id} - ${job.description || 'Training'}`,
              status: job.status,
              progress: job.progress || 0,
              algorithm: job.algorithm || 'XGBoost',
              startedAt: job.started_at ? new Date(job.started_at).toLocaleString() : 'En attente'
            })))
          }
        } catch (e) {
          // Les jobs d'entraînement peuvent ne pas être disponibles
          console.log('Training jobs not available')
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  // Filtrer les modèles selon le statut sélectionné
  useEffect(() => {
    if (statusFilter === 'all') {
      setFilteredModels(models)
    } else {
      setFilteredModels(models.filter((m) => m.status === statusFilter))
    }
  }, [statusFilter, models])

  const activeModel = models.find((m) => m.status === 'active')

  const columns: Column<MLModel>[] = [
    {
      key: 'name',
      label: 'Nom',
      sortable: true,
    },
    {
      key: 'version',
      label: 'Version',
      render: (model) => (
        <Badge variant="info" size="sm">
          {model.version}
        </Badge>
      ),
      sortable: true,
    },
    {
      key: 'status',
      label: 'Statut',
      render: (model) => {
        const statusConfig = {
          active: { label: 'Actif', variant: 'success' as const },
          training: { label: 'Entraînement', variant: 'warning' as const },
          inactive: { label: 'Inactif', variant: 'info' as const },
          archived: { label: 'Archivé', variant: 'warning' as const },
        }
        const config = statusConfig[model.status] || statusConfig.inactive
        return <Badge variant={config.variant}>{config.label}</Badge>
      },
    },
    {
      key: 'accuracy',
      label: 'Précision',
      render: (model) => `${formatMetric(model.accuracy, 1)}%`,
      sortable: true,
    },
    {
      key: 'f1Score',
      label: 'F1 Score',
      render: (model) => formatMetric(model.f1Score, 2),
      sortable: true,
    },
    {
      key: 'trainedAt',
      label: 'Date d\'entraînement',
      render: (model) => new Date(model.trainedAt || Date.now()).toLocaleDateString('fr-FR'),
      sortable: true,
    },
  ]

  const handleActions = (model: MLModel) => (
    <div className="flex items-center gap-2">
      <button
        onClick={() => navigate(`${ROUTES.ML_MODELS}/${model.id}`)}
        className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="Voir détails"
      >
        <span className="material-symbols-outlined text-[20px]">visibility</span>
      </button>
      {model.status !== 'active' && (
        <button
          onClick={async () => {
            try {
              await mlService.activate(model.id)
              const data = await mlService.getAll()
              setModels(data)
            } catch (error) {
              console.error('Erreur lors de l\'activation:', error)
            }
          }}
          className="text-gray-400 hover:text-green-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title="Activer"
        >
          <span className="material-symbols-outlined text-[20px]">check_circle</span>
        </button>
      )}
    </div>
  )

  const handleExport = () => {
    const exportColumns: ExportColumn[] = [
      { key: 'name', label: 'Nom' },
      { key: 'version', label: 'Version' },
      {
        key: 'status',
        label: 'Statut',
        format: (v) => (v === 'active' ? 'Actif' : v === 'training' ? 'Entraînement' : 'Inactif'),
      },
      {
        key: 'accuracy',
        label: 'Précision',
        format: (v) => `${(v * 100).toFixed(1)}%`,
      },
      {
        key: 'f1Score',
        label: 'F1 Score',
        format: (v) => v.toFixed(3),
      },
      {
        key: 'trainedAt',
        label: 'Date d\'entraînement',
        format: (v) => new Date(v).toLocaleDateString('fr-FR'),
      },
    ]

    exportToExcel(
      models,
      exportColumns,
      `modeles-ml-${new Date().toISOString().split('T')[0]}`,
      'Historique des Versions'
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
    <MiseEnPagePrincipale title="Gestion des Modèles ML">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl md:text-4xl font-black tracking-tight text-gray-900 dark:text-white">
              Gestion des Modèles ML
            </h1>
            <p className="text-base text-purple-600 dark:text-purple-400 font-normal max-w-2xl">
              Gérez le cycle de vie des modèles prédictifs, surveillez la dérive des données et déployez de nouvelles versions.
            </p>
          </div>
          <div className="flex gap-3">
            <Bouton variant="outline" onClick={() => setShowCompareModal(true)}>
              <span className="material-symbols-outlined text-[20px]">compare_arrows</span>
              Comparer Versions
            </Bouton>
            <Bouton onClick={() => setShowTrainingModal(true)}>
              <span className="material-symbols-outlined text-[20px]">add</span>
              Nouvel Entraînement
            </Bouton>
          </div>
        </div>

        {/* Active Model Carte */}
        {activeModel && (
          <Carte className="overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-green-600 dark:text-green-400">check_circle</span>
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">Modèle en Production</h2>
                <Badge variant="success" size="sm">ACTIF</Badge>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => {
                    // Télécharger les infos du modèle en JSON
                    const modelData = {
                      id: activeModel.id,
                      name: activeModel.name,
                      version: activeModel.version,
                      accuracy: formatMetric(activeModel.accuracy, 2),
                      f1_score: formatMetric(activeModel.f1Score, 2),
                      precision: formatMetric(activeModel.precision, 2),
                      recall: formatMetric(activeModel.recall, 2),
                      trained_at: activeModel.trainedAt,
                      training_data_size: activeModel.trainingDataSize
                    }
                    const blob = new Blob([JSON.stringify(modelData, null, 2)], { type: 'application/json' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `model-${activeModel.name}-v${activeModel.version}.json`
                    a.click()
                    URL.revokeObjectURL(url)
                  }}
                  className="text-gray-500 hover:text-primary p-1 rounded transition-colors" 
                  title="Télécharger les métadonnées du modèle"
                >
                  <span className="material-symbols-outlined">download</span>
                </button>
                <button 
                  onClick={() => navigate(`${ROUTES.ML_MODELS}/${activeModel.id}`)}
                  className="text-gray-500 hover:text-primary p-1 rounded transition-colors" 
                  title="Voir les détails du modèle"
                >
                  <span className="material-symbols-outlined">settings</span>
                </button>
              </div>
            </div>
            <div className="p-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Version Actuelle</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeModel.version}</p>
                <p className="text-xs text-primary font-medium">Random Forest Classifier</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">F1-Score</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatMetric(activeModel.f1Score, 2)}</p>
                </div>
                <p className="text-xs text-gray-400">Score actuel</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Précision (Accuracy)</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatMetric(activeModel.accuracy, 0)}%</p>
                </div>
                <p className="text-xs text-gray-400">Score actuel</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Dernier Entraînement</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white truncate">
                  {new Date(activeModel.trainedAt || Date.now()).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}
                </p>
                <p className="text-xs text-gray-500">{(activeModel.trainingDataSize ?? 0).toLocaleString()} échantillons</p>
              </div>
            </div>
          </Carte>
        )}

        {/* Performance Chart & Training Jobs */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Performance Chart */}
          <Carte className="lg:col-span-2 flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Performance en Production</h2>
              <select 
                value={periodFilter}
                onChange={(e) => setPeriodFilter(e.target.value as '30' | '7' | '24')}
                className="bg-gray-50 dark:bg-gray-800 border-none text-xs font-medium rounded-lg py-1.5 pl-3 pr-8 focus:ring-1 focus:ring-primary cursor-pointer text-gray-900 dark:text-white"
              >
                <option value="30">30 derniers jours</option>
                <option value="7">7 derniers jours</option>
                <option value="24">24 dernières heures</option>
              </select>
            </div>
            <div className="p-6 flex-1 min-h-[300px]">
              {performanceData.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full py-12">
                  <span className="material-symbols-outlined text-gray-300 dark:text-gray-600 text-[64px] mb-4">bar_chart</span>
                  <p className="text-gray-500 dark:text-gray-400 text-center">
                    Aucune donnée de performance disponible.<br/>
                    <span className="text-sm">Les données apparaîtront après l'entraînement de modèles.</span>
                  </p>
                </div>
              ) : (
                <>
                  <div className="mb-4 flex items-start gap-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-900/30 rounded-lg p-3">
                    <span className="material-symbols-outlined text-blue-600 dark:text-blue-400 text-[20px] mt-0.5">info</span>
                    <div>
                      <p className="text-sm font-bold text-blue-600 dark:text-blue-400">Surveillance des performances</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        La détection de dérive des données (drift) n'est pas encore implémentée.
                        Cette fonctionnalité sera ajoutée dans une prochaine version.
                      </p>
                    </div>
                  </div>
                  <GraphiqueLignes
                    data={performanceData}
                    dataKey="value"
                    lines={[{ key: 'value', name: 'Performance', color: '#7c3bed' }]}
                    xAxisKey="date"
                    height={250}
                  />
                </>
              )}
            </div>
          </Carte>

          {/* Training Jobs */}
          <Carte className="flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Jobs d'Entraînement</h2>
              <Badge variant="primary" size="sm">{trainingJobs.filter(j => j.status === 'running').length} EN COURS</Badge>
            </div>
            <div className="p-6 flex flex-col gap-5 overflow-y-auto max-h-[400px]">
              {trainingJobs.map((job) => (
                <div key={job.id} className="flex flex-col gap-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className={`material-symbols-outlined text-sm ${
                        job.status === 'running' ? 'text-primary animate-spin' : 
                        job.status === 'pending' ? 'text-gray-400' : 
                        'text-red-600'
                      }`}>
                        {job.status === 'running' ? 'sync' : job.status === 'pending' ? 'hourglass_empty' : 'error'}
                      </span>
                      <span className={`text-sm font-bold ${
                        job.status === 'failed' ? 'text-red-600' : 'text-gray-900 dark:text-white'
                      }`}>
                        {job.name}
                      </span>
                    </div>
                    <span className="text-xs font-medium text-gray-500">
                      {job.status === 'running' ? `${job.progress}%` : job.status === 'pending' ? 'En attente' : 'Échec'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${
                        job.status === 'running' ? 'bg-primary' : 
                        job.status === 'failed' ? 'bg-red-600' : 
                        'bg-gray-400'
                      }`}
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Algorithme: {job.algorithm} • {job.startedAt}
                  </p>
                </div>
              ))}
            </div>
            <div className="mt-auto px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
              <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                {trainingJobs.length > 0 ? `${trainingJobs.length} job(s) affichés` : 'Aucun job en cours'}
              </p>
            </div>
          </Carte>
        </div>

        {/* Models Table */}
        <Carte>
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex flex-wrap gap-4 justify-between items-center">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Historique des Versions</h2>
            <div className="flex gap-2 items-center">
              <div className="relative">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="pl-10 pr-8 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-white appearance-none cursor-pointer focus:ring-2 focus:ring-primary/50 focus:border-primary"
                >
                  <option value="all">Tous les statuts</option>
                  <option value="active">Actifs</option>
                  <option value="inactive">Inactifs</option>
                  <option value="archived">Archivés</option>
                  <option value="training">En entraînement</option>
                </select>
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 material-symbols-outlined text-[18px] pointer-events-none">
                  filter_list
                </span>
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 material-symbols-outlined text-[16px] pointer-events-none">
                  expand_more
                </span>
              </div>
              <button
                onClick={handleExport}
                className="text-gray-500 hover:text-primary transition-colors flex items-center gap-1 text-sm font-medium"
              >
                <span className="material-symbols-outlined text-[18px]">download</span>
                Exporter
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <TableauDonnees
              data={filteredModels}
              columns={columns}
              actions={handleActions}
              emptyMessage={statusFilter === 'archived' ? 'Aucun modèle archivé' : 'Aucun modèle trouvé'}
            />
          </div>
        </Carte>
      </div>

      {/* Modale d'entraînement */}
      <ModaleEntrainement
        isOpen={showTrainingModal}
        onClose={() => setShowTrainingModal(false)}
        onSuccess={async () => {
          setShowTrainingModal(false)
          // Recharger les modèles après entraînement
          const data = await mlService.getAll()
          setModels(data)
        }}
      />

      {/* Modale de comparaison des versions */}
      {showCompareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Comparer les Versions</h2>
              <button
                onClick={() => setShowCompareModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Sélectionnez deux modèles à comparer :
              </p>
              <div className="grid grid-cols-2 gap-4 mb-6">
                {models.slice(0, 6).map((model) => (
                  <label
                    key={model.id}
                    className={`flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedModels.includes(model.id)
                        ? 'border-primary bg-primary/5'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary/50'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedModels.includes(model.id)}
                      onChange={(e) => {
                        if (e.target.checked && selectedModels.length < 2) {
                          setSelectedModels([...selectedModels, model.id])
                        } else if (!e.target.checked) {
                          setSelectedModels(selectedModels.filter((id) => id !== model.id))
                        }
                      }}
                      disabled={!selectedModels.includes(model.id) && selectedModels.length >= 2}
                      className="w-4 h-4 text-primary rounded"
                    />
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 dark:text-white">{model.name}</p>
                      <p className="text-sm text-gray-500">v{model.version} - {formatMetric(model.accuracy, 1)}%</p>
                    </div>
                    {model.status === 'active' && <Badge variant="success" size="sm">ACTIF</Badge>}
                  </label>
                ))}
              </div>

              {selectedModels.length === 2 && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="font-bold text-gray-900 dark:text-white mb-4">Comparaison</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                          <th className="pb-2">Métrique</th>
                          {selectedModels.map((id) => {
                            const m = models.find((model) => model.id === id)
                            return <th key={id} className="pb-2">{m?.name} v{m?.version}</th>
                          })}
                          <th className="pb-2">Différence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                        {['accuracy', 'f1Score', 'precision', 'recall'].map((metric) => {
                          const vals = selectedModels.map((id) => {
                            const m = models.find((model) => model.id === id)
                            return parseFloat(formatMetric((m as any)?.[metric], 2))
                          })
                          const diff = vals[1] - vals[0]
                          return (
                            <tr key={metric}>
                              <td className="py-2 font-medium text-gray-700 dark:text-gray-300 capitalize">{metric === 'f1Score' ? 'F1 Score' : metric}</td>
                              {vals.map((v, i) => (
                                <td key={i} className="py-2 text-gray-900 dark:text-white">{v}%</td>
                              ))}
                              <td className={`py-2 font-semibold ${diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                                {diff > 0 ? '+' : ''}{diff.toFixed(2)}%
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 mt-6">
                <Bouton variant="outline" onClick={() => { setShowCompareModal(false); setSelectedModels([]); }}>
                  Fermer
                </Bouton>
              </div>
            </div>
          </div>
        </div>
      )}
    </MiseEnPagePrincipale>
  )
}
