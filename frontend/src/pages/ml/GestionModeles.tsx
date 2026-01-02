import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import Carte from '@/components/common/Carte'
import GraphiqueLignes from '@/components/charts/GraphiqueLignes'
import { mlService, MLModel } from '@/api/services/mlService'
import { ROUTES } from '@/utils/constants'
import { exportToExcel, type ExportColumn } from '@/utils/exportService'

interface TrainingJob {
  id: string
  name: string
  status: 'running' | 'pending' | 'completed' | 'failed'
  progress: number
  algorithm: string
  startedAt: string
}

export default function GestionModeles() {
  const navigate = useNavigate()
  const [models, setModels] = useState<MLModel[]>([])
  const [loading, setLoading] = useState(true)
  const [trainingJobs] = useState<TrainingJob[]>([
    {
      id: '1024',
      name: 'Job #1024 - Retraining',
      status: 'running',
      progress: 65,
      algorithm: 'XGBoost',
      startedAt: 'Il y a 2h',
    },
    {
      id: '1025',
      name: 'Job #1025 - Eval Set B',
      status: 'pending',
      progress: 0,
      algorithm: 'Random Forest',
      startedAt: 'En attente',
    },
  ])

  const [performanceData] = useState([
    { date: '1 Oct', value: 60 },
    { date: '5 Oct', value: 62 },
    { date: '10 Oct', value: 65 },
    { date: '15 Oct', value: 68 },
    { date: '20 Oct', value: 70 },
    { date: '22 Oct', value: 72 },
    { date: '24 Oct', value: 75 },
    { date: '26 Oct', value: 70 },
  ])

  useEffect(() => {
    const loadModels = async () => {
      setLoading(true)
      try {
        const data = await mlService.getAll()
        setModels(data)
      } catch (error) {
        console.error('Erreur lors du chargement des modèles:', error)
      } finally {
        setLoading(false)
      }
    }
    loadModels()
  }, [])

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
      render: (model) => (
        <Badge
          variant={
            model.status === 'active'
              ? 'success'
              : model.status === 'training'
              ? 'warning'
              : 'info'
          }
        >
          {model.status === 'active'
            ? 'Actif'
            : model.status === 'training'
            ? 'Entraînement'
            : 'Inactif'}
        </Badge>
      ),
    },
    {
      key: 'accuracy',
      label: 'Précision',
      render: (model) => `${(model.accuracy * 100).toFixed(1)}%`,
      sortable: true,
    },
    {
      key: 'f1Score',
      label: 'F1 Score',
      render: (model) => (model.f1Score ?? 0).toFixed(3),
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
            <Bouton variant="outline">
              <span className="material-symbols-outlined text-[20px]">compare_arrows</span>
              Comparer Versions
            </Bouton>
            <Bouton>
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
                <button className="text-gray-500 hover:text-primary p-1 rounded transition-colors" title="Télécharger">
                  <span className="material-symbols-outlined">download</span>
                </button>
                <button className="text-gray-500 hover:text-primary p-1 rounded transition-colors" title="Paramètres">
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
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{(activeModel.f1Score ?? 0).toFixed(2)}</p>
                  <span className="flex items-center text-xs font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 rounded">
                    <span className="material-symbols-outlined text-[14px] mr-0.5">trending_up</span>
                    +2.4%
                  </span>
                </div>
                <p className="text-xs text-gray-400">vs v2.3</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Précision (Accuracy)</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{(activeModel.accuracy * 100).toFixed(0)}%</p>
                  <span className="flex items-center text-xs font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 rounded">
                    <span className="material-symbols-outlined text-[14px] mr-0.5">trending_up</span>
                    +1.1%
                  </span>
                </div>
                <p className="text-xs text-gray-400">vs v2.3</p>
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
              <select className="bg-gray-50 dark:bg-gray-800 border-none text-xs font-medium rounded-lg py-1.5 pl-3 pr-8 focus:ring-1 focus:ring-primary cursor-pointer text-gray-900 dark:text-white">
                <option>30 derniers jours</option>
                <option>7 derniers jours</option>
                <option>24 dernières heures</option>
              </select>
            </div>
            <div className="p-6 flex-1 min-h-[300px]">
              <div className="mb-4 flex items-start gap-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/30 rounded-lg p-3">
                <span className="material-symbols-outlined text-red-600 dark:text-red-400 text-[20px] mt-0.5">warning</span>
                <div>
                  <p className="text-sm font-bold text-red-600 dark:text-red-400">Dérive des données détectée (Drift)</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    La distribution de la caractéristique <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-gray-800 dark:text-gray-200">taux_assiduite</code> a changé significativement depuis hier.
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
              <button className="w-full text-sm font-semibold text-primary hover:text-purple-700 dark:hover:text-purple-300 transition-colors flex items-center justify-center gap-2">
                Voir tous les jobs
                <span className="material-symbols-outlined text-base">arrow_forward</span>
              </button>
            </div>
          </Carte>
        </div>

        {/* Models Table */}
        <Carte>
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex flex-wrap gap-4 justify-between items-center">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Historique des Versions</h2>
            <div className="flex gap-2">
              <button className="text-gray-500 hover:text-primary transition-colors flex items-center gap-1 text-sm font-medium">
                <span className="material-symbols-outlined text-[18px]">filter_list</span>
                Filtrer
              </button>
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
              data={models}
              columns={columns}
              actions={handleActions}
              emptyMessage="Aucun modèle trouvé"
            />
          </div>
        </Carte>
      </div>
    </MiseEnPagePrincipale>
  )
}
