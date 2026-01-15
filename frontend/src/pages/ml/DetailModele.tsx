import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import GraphiqueROC from '@/components/charts/GraphiqueROC'
import ModaleEntrainement from '@/components/modals/ModaleEntrainement'
import ModaleConfirmation from '@/components/common/ModaleConfirmation'
import { mlService, MLModel } from '@/api/services/mlService'
import { ROUTES } from '@/utils/constants'

// Helper pour normaliser les métriques (si > 1, c'est déjà en %)
const formatMetric = (value: number | string | undefined, decimals: number = 1): string => {
  if (value === undefined || value === null || value === '') return '0'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue)) return '0'
  // Si la valeur est > 1, elle est déjà en pourcentage (0-100 scale)
  const normalized = numValue > 1 ? numValue : numValue * 100
  return normalized.toFixed(decimals)
}

// Helper pour calculer le changement de métrique par rapport au modèle précédent
const calculateMetricChange = (
  current: number | string | undefined,
  previous: number | string | undefined
): { value: number; isPositive: boolean } | null => {
  if (!current || !previous) return null
  const currentNum = typeof current === 'string' ? parseFloat(current) : current
  const previousNum = typeof previous === 'string' ? parseFloat(previous) : previous
  if (isNaN(currentNum) || isNaN(previousNum)) return null
  
  const currentNorm = currentNum > 1 ? currentNum : currentNum * 100
  const previousNorm = previousNum > 1 ? previousNum : previousNum * 100
  
  const change = currentNorm - previousNorm
  return {
    value: Math.abs(change),
    isPositive: change >= 0,
  }
}

export default function DetailModele() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [model, setModel] = useState<MLModel | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('metrics')
  const [showRetrainModal, setShowRetrainModal] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [archiveConfirmation, setArchiveConfirmation] = useState(false)
  const [deployConfirmation, setDeployConfirmation] = useState(false)
  const [previousModel, setPreviousModel] = useState<MLModel | null>(null)

  useEffect(() => {
    const loadModel = async () => {
      if (!id) return
      setLoading(true)
      try {
        const data = await mlService.getById(id)
        if (!data) {
          toast.error('Modèle non trouvé')
          return
        }
        // Charger le modèle précédent pour comparer les métriques
        if (data.version) {
          try {
            const allModels = await mlService.getAll()
            const currentIndex = allModels.findIndex(m => m.id === id)
            if (currentIndex > 0) {
              setPreviousModel(allModels[currentIndex - 1])
            }
          } catch (err) {
            console.error('Erreur lors du chargement du modèle précédent:', err)
          }
        }
        setModel(data)
      } catch (error) {
        console.error('Erreur lors du chargement du modèle:', error)
        toast.error('Erreur lors du chargement du modèle')
      } finally {
        setLoading(false)
      }
    }
    loadModel()
  }, [id])

  const handleRetrain = () => {
    setShowRetrainModal(true)
  }

  const handleArchive = async () => {
    if (!model || !id) return
    setArchiveConfirmation(true)
  }

  const confirmArchive = async () => {
    if (!model || !id) return
    setActionLoading('archive')
    try {
      await mlService.archive(id)
      toast.success(`Modèle ${model.version} archivé avec succès`)
      navigate(ROUTES.ML_MODELS)
    } catch (error: any) {
      console.error('Erreur lors de l\'archivage:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Erreur lors de l\'archivage du modèle'
      toast.error(errorMessage)
    } finally {
      setActionLoading(null)
      setArchiveConfirmation(false)
    }
  }

  const handleDeploy = async () => {
    if (!model || !id) return
    setDeployConfirmation(true)
  }

  const confirmDeploy = async () => {
    if (!model || !id) return
    setActionLoading('deploy')
    try {
      await mlService.activate(id)
      toast.success(`Modèle ${model.version} déployé en production !`)
      // Recharger le modèle pour mettre à jour le statut
      const data = await mlService.getById(id)
      setModel(data)
    } catch (error) {
      console.error('Erreur lors du déploiement:', error)
      toast.error('Erreur lors du déploiement du modèle')
    } finally {
      setActionLoading(null)
      setDeployConfirmation(false)
    }
  }

  const handleTrainingSuccess = () => {
    setShowRetrainModal(false)
    // Recharger pour voir le nouveau modèle
    if (id) {
      mlService.getById(id).then(setModel).catch(console.error)
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

  if (!model) {
    return (
      <MiseEnPagePrincipale>
        <div className="mx-auto max-w-7xl">
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Modèle non trouvé
            </h2>
            <Bouton onClick={() => navigate(ROUTES.ML_MODELS)}>Retour à la liste</Bouton>
          </div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  const tabs = [
    { id: 'metrics', label: 'Métriques' },
    { id: 'features', label: 'Features' },
    { id: 'confusion', label: 'Confusion' },
    { id: 'shap', label: 'SHAP' },
    { id: 'export', label: 'Export' },
  ]

  return (
    <MiseEnPagePrincipale title={`Détails Modèle ${model.version}`}>
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Breadcrumbs */}
        <nav className="flex items-center text-sm text-purple-600 dark:text-purple-400">
          <button onClick={() => navigate(ROUTES.ML_MODELS)} className="hover:text-primary">
            Modèles
          </button>
          <span className="mx-2">/</span>
          <button onClick={() => navigate(ROUTES.ML_MODELS)} className="hover:text-primary">
            Liste des modèles
          </button>
          <span className="mx-2">/</span>
          <span className="text-gray-900 dark:text-white font-semibold">Détails {model.version}</span>
        </nav>

        {/* Page Header & Actions */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
              Modèle {model.version}
        </h1>
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 rounded-full bg-green-500"></span>
              <p className="text-purple-600 dark:text-purple-400 text-sm font-medium">
                Statut: <span className="text-gray-900 dark:text-white">{model.status === 'active' ? 'Déployé (Production)' : 'Inactif'}</span>
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Bouton variant="outline" onClick={handleRetrain} disabled={actionLoading !== null}>
              <span className="material-symbols-outlined text-[20px] mr-2">history</span>
              Réentraîner
            </Bouton>
            <Bouton variant="outline" onClick={handleArchive} disabled={actionLoading !== null}>
              {actionLoading === 'archive' ? (
                <span className="material-symbols-outlined text-[20px] mr-2 animate-spin">sync</span>
              ) : (
                <span className="material-symbols-outlined text-[20px] mr-2">archive</span>
              )}
              Archiver
            </Bouton>
            {model.status === 'active' ? (
              <Bouton variant="primary" disabled>
                <span className="material-symbols-outlined text-[20px] mr-2">rocket_launch</span>
                Déjà déployé
              </Bouton>
            ) : (
              <Bouton onClick={handleDeploy} disabled={actionLoading !== null}>
                {actionLoading === 'deploy' ? (
                  <span className="material-symbols-outlined text-[20px] mr-2 animate-spin">sync</span>
                ) : (
                  <span className="material-symbols-outlined text-[20px] mr-2">rocket_launch</span>
                )}
                Déployer
              </Bouton>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex gap-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`border-b-[3px] pb-3 px-1 text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'border-primary text-primary font-bold'
                    : 'border-transparent text-purple-600 dark:text-purple-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* KPI Cartes - Affichées uniquement dans l'onglet Métriques */}
        {activeTab === 'metrics' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Carte>
              <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">Accuracy</p>
              <div className="flex items-baseline gap-2">
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {formatMetric(model.accuracy, 1)}%
                </h3>
                {(() => {
                  const change = calculateMetricChange(model.accuracy, previousModel?.accuracy)
                  if (!change) return null
                  return (
                    <span className={`flex items-center text-xs font-bold px-1.5 py-0.5 rounded ${
                      change.isPositive
                        ? 'text-green-600 bg-green-100 dark:bg-green-900/30'
                        : 'text-red-500 bg-red-100 dark:bg-red-900/30'
                    }`}>
                      <span className="material-symbols-outlined text-[14px]">
                        {change.isPositive ? 'trending_up' : 'trending_down'}
                      </span>
                      {change.value.toFixed(1)}%
                    </span>
                  )
                })()}
              </div>
            </Carte>
            <Carte>
              <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">Précision</p>
              <div className="flex items-baseline gap-2">
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {formatMetric(model.precision, 1)}%
                </h3>
                {(() => {
                  const change = calculateMetricChange(model.precision, previousModel?.precision)
                  if (!change) return null
                  return (
                    <span className={`flex items-center text-xs font-bold px-1.5 py-0.5 rounded ${
                      change.isPositive
                        ? 'text-green-600 bg-green-100 dark:bg-green-900/30'
                        : 'text-red-500 bg-red-100 dark:bg-red-900/30'
                    }`}>
                      <span className="material-symbols-outlined text-[14px]">
                        {change.isPositive ? 'trending_up' : 'trending_down'}
                      </span>
                      {change.value.toFixed(1)}%
                    </span>
                  )
                })()}
              </div>
            </Carte>
            <Carte>
              <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">Rappel (Recall)</p>
              <div className="flex items-baseline gap-2">
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {formatMetric(model.recall, 1)}%
                </h3>
                {(() => {
                  const change = calculateMetricChange(model.recall, previousModel?.recall)
                  if (!change) return null
                  return (
                    <span className={`flex items-center text-xs font-bold px-1.5 py-0.5 rounded ${
                      change.isPositive
                        ? 'text-green-600 bg-green-100 dark:bg-green-900/30'
                        : 'text-red-500 bg-red-100 dark:bg-red-900/30'
                    }`}>
                      <span className="material-symbols-outlined text-[14px]">
                        {change.isPositive ? 'trending_up' : 'trending_down'}
                      </span>
                      {change.value.toFixed(1)}%
                    </span>
                  )
                })()}
              </div>
            </Carte>
            <Carte>
              <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">F1-Score</p>
              <div className="flex items-baseline gap-2">
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {formatMetric(model.f1Score, 2)}
                </h3>
                {(() => {
                  const change = calculateMetricChange(model.f1Score, previousModel?.f1Score)
                  if (!change) return null
                  return (
                    <span className={`flex items-center text-xs font-bold px-1.5 py-0.5 rounded ${
                      change.isPositive
                        ? 'text-green-600 bg-green-100 dark:bg-green-900/30'
                        : 'text-red-500 bg-red-100 dark:bg-red-900/30'
                    }`}>
                      <span className="material-symbols-outlined text-[14px]">
                        {change.isPositive ? 'trending_up' : 'trending_down'}
                      </span>
                      {change.value.toFixed(1)}%
                    </span>
                  )
                })()}
              </div>
            </Carte>
          </div>
        )}

        {/* Contenu des onglets */}
        {activeTab === 'metrics' && (
          <>
            {/* Chart & Info Split */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* ROC Curve */}
              <Carte className="lg:col-span-2 flex flex-col">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">Courbe ROC</h3>
                    <p className="text-sm text-purple-600 dark:text-purple-400">Performance globale du classificateur binaire</p>
                  </div>
                  <div className="px-3 py-1 rounded bg-primary/10 text-primary font-bold text-sm">
                    AUC: {formatMetric(model.auc ?? 0.94, 2)}
                  </div>
                </div>
                <div className="w-full" style={{ height: '300px', minHeight: '300px' }}>
                  <GraphiqueROC 
                    data={model.rocCurve ? {
                      fpr: model.rocCurve.fpr,
                      tpr: model.rocCurve.tpr,
                      thresholds: model.rocCurve.thresholds,
                      auc: model.auc ?? 0.94
                    } : undefined}
                    height={300}
                    showOptimalThreshold={true}
                  />
                </div>
              </Carte>

          {/* Training Info */}
          <Carte className="h-full">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Informations d'entraînement</h3>
            <div className="flex flex-col gap-5">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded bg-purple-50 dark:bg-purple-900/20 text-primary">
                  <span className="material-symbols-outlined text-[20px]">psychology</span>
                </div>
                <div>
                  <p className="text-xs text-purple-600 dark:text-purple-400">Algorithme</p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">RandomForestClassifier</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="p-2 rounded bg-purple-50 dark:bg-purple-900/20 text-primary">
                  <span className="material-symbols-outlined text-[20px]">schedule</span>
                </div>
                <div>
                  <p className="text-xs text-purple-600 dark:text-purple-400">Date</p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {new Date(model.trainedAt || Date.now()).toLocaleDateString('fr-FR', { 
                      day: 'numeric', 
                      month: 'short', 
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="p-2 rounded bg-purple-50 dark:bg-purple-900/20 text-primary">
                  <span className="material-symbols-outlined text-[20px]">dataset</span>
                </div>
                <div>
                  <p className="text-xs text-purple-600 dark:text-purple-400">Échantillons</p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {(model.trainingDataSize ?? 0).toLocaleString()} étudiants
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="p-2 rounded bg-purple-50 dark:bg-purple-900/20 text-primary">
                  <span className="material-symbols-outlined text-[20px]">view_column</span>
                </div>
                <div>
                  <p className="text-xs text-purple-600 dark:text-purple-400">Features</p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">24</p>
                </div>
              </div>
            </div>
          </Carte>
        </div>

            {/* Metrics Table */}
            <Carte>
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Métriques par Classe</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-900/50 text-purple-600 dark:text-purple-400 font-medium">
                    <tr>
                      <th className="px-6 py-4">Classe</th>
                      <th className="px-6 py-4">Précision</th>
                      <th className="px-6 py-4">Rappel</th>
                      <th className="px-6 py-4">F1-Score</th>
                      <th className="px-6 py-4">Support</th>
                      <th className="px-6 py-4 text-right">Performance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-4 font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500"></span>
                        Succès (1)
                      </td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">0.94</td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">0.96</td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">0.95</td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">8,200</td>
                      <td className="px-6 py-4 text-right">
                        <div className="w-24 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full inline-block overflow-hidden">
                          <div className="h-full bg-green-500 w-[95%]"></div>
                        </div>
                      </td>
                    </tr>
                    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-4 font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-red-400"></span>
                        Échec (0)
                      </td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">0.89</td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">0.82</td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">0.85</td>
                      <td className="px-6 py-4 text-gray-900 dark:text-gray-300">4,250</td>
                      <td className="px-6 py-4 text-right">
                        <div className="w-24 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full inline-block overflow-hidden">
                          <div className="h-full bg-red-400 w-[85%]"></div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Carte>
          </>
        )}

        {activeTab === 'features' && (
          <Carte>
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Features Importantes</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Top features les plus importantes pour ce modèle</p>
            </div>
            <div className="p-6">
              {model.featureImportance && model.featureImportance.length > 0 ? (
                <div className="space-y-4">
                  {model.featureImportance.slice(0, 20).map((feature, index) => (
                    <div key={feature.name} className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-gray-900 dark:text-white">{feature.name}</span>
                          <span className="text-sm text-gray-600 dark:text-gray-400">{feature.category || 'Feature'}</span>
                        </div>
                        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary"
                            style={{ width: `${(typeof feature.importance === 'string' ? parseFloat(feature.importance) : feature.importance) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Importance: {((typeof feature.importance === 'string' ? parseFloat(feature.importance) : feature.importance) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <span className="material-symbols-outlined text-6xl mb-4">analytics</span>
                  <p>Données d'importance des features non disponibles</p>
                  <p className="text-sm mt-2">Ces données seront disponibles après l'entraînement du modèle</p>
                </div>
              )}
            </div>
          </Carte>
        )}

        {activeTab === 'confusion' && (
          <Carte>
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Matrice de Confusion</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Visualisation des prédictions correctes et incorrectes</p>
            </div>
            <div className="p-6">
              {model.confusionMatrix ? (
                <div className="max-w-md mx-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr>
                        <th className="p-4"></th>
                        <th className="p-4 text-center font-semibold text-gray-900 dark:text-white">Prédit: Échec</th>
                        <th className="p-4 text-center font-semibold text-gray-900 dark:text-white">Prédit: Succès</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="p-4 font-semibold text-gray-900 dark:text-white text-right">Réel: Échec</td>
                        <td className="p-4 bg-green-100 dark:bg-green-900/30 text-center font-bold text-green-700 dark:text-green-400">
                          {model.confusionMatrix.tn?.toLocaleString() ?? 'N/A'}
                          <div className="text-xs font-normal text-gray-600 dark:text-gray-400 mt-1">Vrais Négatifs</div>
                        </td>
                        <td className="p-4 bg-orange-100 dark:bg-orange-900/30 text-center font-bold text-orange-700 dark:text-orange-400">
                          {model.confusionMatrix.fp?.toLocaleString() ?? 'N/A'}
                          <div className="text-xs font-normal text-gray-600 dark:text-gray-400 mt-1">Faux Positifs</div>
                        </td>
                      </tr>
                      <tr>
                        <td className="p-4 font-semibold text-gray-900 dark:text-white text-right">Réel: Succès</td>
                        <td className="p-4 bg-orange-100 dark:bg-orange-900/30 text-center font-bold text-orange-700 dark:text-orange-400">
                          {model.confusionMatrix.fn?.toLocaleString() ?? 'N/A'}
                          <div className="text-xs font-normal text-gray-600 dark:text-gray-400 mt-1">Faux Négatifs</div>
                        </td>
                        <td className="p-4 bg-green-100 dark:bg-green-900/30 text-center font-bold text-green-700 dark:text-green-400">
                          {model.confusionMatrix.tp?.toLocaleString() ?? 'N/A'}
                          <div className="text-xs font-normal text-gray-600 dark:text-gray-400 mt-1">Vrais Positifs</div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <span className="material-symbols-outlined text-6xl mb-4">grid_on</span>
                  <p>Matrice de confusion non disponible</p>
                  <p className="text-sm mt-2">Ces données seront générées lors du prochain entraînement</p>
                </div>
              )}
            </div>
          </Carte>
        )}

        {activeTab === 'shap' && (
          <Carte>
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Analyse SHAP</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">SHAP (SHapley Additive exPlanations) - Explication des prédictions</p>
            </div>
            <div className="p-6">
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <span className="material-symbols-outlined text-6xl mb-4">bar_chart</span>
                <p>Graphique SHAP en cours de développement</p>
                <p className="text-sm mt-2">Les valeurs SHAP seront disponibles après le prochain entraînement</p>
              </div>
            </div>
          </Carte>
        )}

        {activeTab === 'export' && (
          <Carte>
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Exporter le Modèle</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Téléchargez les métadonnées et les artefacts du modèle</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <Bouton
                  variant="outline"
                  onClick={() => {
                    const modelData = {
                      id: model.id,
                      name: model.name,
                      version: model.version,
                      accuracy: formatMetric(model.accuracy, 2),
                      precision: formatMetric(model.precision, 2),
                      recall: formatMetric(model.recall, 2),
                      f1_score: formatMetric(model.f1Score, 2),
                      auc: formatMetric(model.auc, 2),
                      trained_at: model.trainedAt,
                      training_data_size: model.trainingDataSize,
                    }
                    const blob = new Blob([JSON.stringify(modelData, null, 2)], { type: 'application/json' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `model-${model.name}-v${model.version}.json`
                    a.click()
                    URL.revokeObjectURL(url)
                    toast.success('Métadonnées du modèle exportées avec succès')
                  }}
                  className="w-full"
                >
                  <span className="material-symbols-outlined text-[20px] mr-2">download</span>
                  Exporter les métadonnées (JSON)
                </Bouton>
                <Bouton
                  variant="outline"
                  onClick={() => {
                    toast.info('Export du modèle complet en cours de développement')
                  }}
                  className="w-full"
                >
                  <span className="material-symbols-outlined text-[20px] mr-2">file_download</span>
                  Exporter le modèle complet (PKL)
                </Bouton>
                <Bouton
                  variant="outline"
                  onClick={() => {
                    toast.info('Rapport PDF en cours de développement')
                  }}
                  className="w-full"
                >
                  <span className="material-symbols-outlined text-[20px] mr-2">picture_as_pdf</span>
                  Générer un rapport PDF
                </Bouton>
              </div>
            </div>
          </Carte>
        )}
      </div>

      {/* Modale Réentraînement */}
      <ModaleEntrainement
        isOpen={showRetrainModal}
        onClose={() => setShowRetrainModal(false)}
        onSuccess={handleTrainingSuccess}
      />

      {/* Modale Confirmation Archivage */}
      <ModaleConfirmation
        isOpen={archiveConfirmation}
        onClose={() => setArchiveConfirmation(false)}
        onConfirm={confirmArchive}
        title="Archiver le modèle"
        message={`Êtes-vous sûr de vouloir archiver le modèle ${model?.version} ? Cette action est irréversible.`}
        confirmText="Archiver"
        cancelText="Annuler"
        variant="warning"
      />

      {/* Modale Confirmation Déploiement */}
      <ModaleConfirmation
        isOpen={deployConfirmation}
        onClose={() => setDeployConfirmation(false)}
        onConfirm={confirmDeploy}
        title="Déployer le modèle"
        message={`Êtes-vous sûr de vouloir déployer le modèle ${model?.version} en production ?`}
        confirmText="Déployer"
        cancelText="Annuler"
        variant="info"
      />
    </MiseEnPagePrincipale>
  )
}
