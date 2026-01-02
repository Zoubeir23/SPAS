import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import { mlService, MLModel } from '@/api/services/mlService'
import { ROUTES } from '@/utils/constants'

export default function DetailModele() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [model, setModel] = useState<MLModel | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('metrics')

  useEffect(() => {
    const loadModel = async () => {
      if (!id) return
      setLoading(true)
      try {
        const data = await mlService.getById(id)
        setModel(data)
      } catch (error) {
        console.error('Erreur lors du chargement du modèle:', error)
      } finally {
        setLoading(false)
      }
    }
    loadModel()
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
            <Bouton variant="outline">
              <span className="material-symbols-outlined text-[20px] mr-2">history</span>
              Réentraîner
            </Bouton>
            <Bouton variant="outline">
              <span className="material-symbols-outlined text-[20px] mr-2">archive</span>
              Archiver
            </Bouton>
            <Bouton>
              <span className="material-symbols-outlined text-[20px] mr-2">rocket_launch</span>
              Déployer
            </Bouton>
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

        {/* KPI Cartes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Carte>
            <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">Accuracy</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                {(model.accuracy * 100).toFixed(1)}%
              </h3>
              <span className="flex items-center text-xs font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 rounded">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> 2.1%
              </span>
            </div>
          </Carte>
          <Carte>
            <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">Précision</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                {(model.precision * 100).toFixed(1)}%
              </h3>
              <span className="flex items-center text-xs font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 rounded">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> 0.8%
              </span>
            </div>
          </Carte>
          <Carte>
            <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">Rappel (Recall)</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                {(model.recall * 100).toFixed(1)}%
              </h3>
              <span className="flex items-center text-xs font-bold text-red-500 bg-red-100 dark:bg-red-900/30 px-1.5 py-0.5 rounded">
                <span className="material-symbols-outlined text-[14px]">trending_down</span> 1.2%
              </span>
            </div>
          </Carte>
          <Carte>
            <p className="text-purple-600 dark:text-purple-400 text-sm font-medium mb-1">F1-Score</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
                {(model.f1Score ?? 0).toFixed(3)}
              </h3>
              <span className="flex items-center text-xs font-bold text-green-600 bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 rounded">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> 0.5%
              </span>
            </div>
          </Carte>
        </div>

        {/* Chart & Info Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ROC Curve Placeholder */}
          <Carte className="lg:col-span-2 flex flex-col min-h-[400px]">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Courbe ROC</h3>
                <p className="text-sm text-purple-600 dark:text-purple-400">Performance globale du classificateur binaire</p>
              </div>
              <div className="px-3 py-1 rounded bg-primary/10 text-primary font-bold text-sm">
                AUC: 0.96
              </div>
            </div>
            <div className="flex-1 w-full flex items-center justify-center bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-dashed border-gray-300 dark:border-gray-700">
              <p className="text-gray-500 dark:text-gray-400">Graphique ROC - À implémenter avec Recharts</p>
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
      </div>
    </MiseEnPagePrincipale>
  )
}
