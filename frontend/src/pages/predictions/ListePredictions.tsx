import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import { predictionService, Prediction } from '@/api/services/predictionService'

export default function ListePredictions() {
  const navigate = useNavigate()
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPredictions()
  }, [])

  const loadPredictions = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await predictionService.getAll()
      setPredictions(data)
    } catch (err) {
      console.error('Erreur lors du chargement des prédictions:', err)
      setError('Impossible de charger les prédictions')
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePredictions = async () => {
    try {
      setLoading(true)
      await predictionService.generatePredictions()
      await loadPredictions()
    } catch (err) {
      console.error('Erreur lors de la génération des prédictions:', err)
      setError('Impossible de générer les prédictions')
    }
  }

  const getRiskVariant = (level: string): 'success' | 'warning' | 'danger' | 'info' => {
    switch (level) {
      case 'low':
        return 'success'
      case 'medium':
        return 'warning'
      case 'high':
        return 'danger'
      default:
        return 'info'
    }
  }

  const getRiskLabel = (level: string): string => {
    switch (level) {
      case 'low':
        return 'Faible'
      case 'medium':
        return 'Moyen'
      case 'high':
        return 'Élevé'
      default:
        return level
    }
  }

  const columns: Column<Prediction>[] = [
    {
      key: 'student_name',
      label: 'Étudiant',
      sortable: true,
      render: (prediction) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900 dark:text-white">
            {prediction.student_name || prediction.studentName || 'N/A'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {prediction.student_matricule || prediction.studentMatricule || ''}
          </span>
        </div>
      ),
    },
    {
      key: 'risk_score',
      label: 'Score de Risque',
      sortable: true,
      render: (prediction) => {
        const score = prediction.risk_score || prediction.riskScore || 0
        return (
          <div className="flex items-center gap-2">
            <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  score > 70 ? 'bg-red-500' : score > 40 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
            <span className="text-sm font-medium">{score}%</span>
          </div>
        )
      },
    },
    {
      key: 'risk_level',
      label: 'Niveau de Risque',
      render: (prediction) => {
        const level = prediction.risk_level || prediction.riskLevel || 'low'
        return (
          <Badge variant={getRiskVariant(level)}>
            {getRiskLabel(level)}
          </Badge>
        )
      },
    },
    {
      key: 'predicted_success_rate',
      label: 'Taux de Réussite Prédit',
      sortable: true,
      render: (prediction) => {
        const rate = prediction.predicted_success_rate || prediction.predictedSuccessRate || 0
        return <span className="font-medium">{rate}%</span>
      },
    },
    {
      key: 'created_at',
      label: 'Date',
      sortable: true,
      render: (prediction) => {
        const date = prediction.created_at || prediction.createdAt
        return date ? new Date(date).toLocaleDateString('fr-FR', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        }) : 'N/A'
      },
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (prediction) => (
        <Bouton
          variant="secondary"
          size="sm"
          onClick={() => navigate(`/predictions/${prediction.id}`)}
        >
          Détails
        </Bouton>
      ),
    },
  ]

  if (loading) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  return (
    <MiseEnPagePrincipale title="Prédictions">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Prédictions de Risque
            </h1>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              Analyse prédictive du risque d'abandon pour chaque étudiant
            </p>
          </div>
          <Bouton onClick={handleGeneratePredictions} disabled={loading}>
            <span className="material-symbols-outlined mr-2">auto_awesome</span>
            Générer les Prédictions
          </Bouton>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <span className="material-symbols-outlined text-blue-600 dark:text-blue-400">analytics</span>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{predictions.length}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Prédictions</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <span className="material-symbols-outlined text-red-600 dark:text-red-400">warning</span>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {predictions.filter(p => (p.risk_level || p.riskLevel) === 'high').length}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Risque Élevé</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                <span className="material-symbols-outlined text-yellow-600 dark:text-yellow-400">schedule</span>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {predictions.filter(p => (p.risk_level || p.riskLevel) === 'medium').length}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Risque Moyen</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <span className="material-symbols-outlined text-green-600 dark:text-green-400">check_circle</span>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {predictions.filter(p => (p.risk_level || p.riskLevel) === 'low').length}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Risque Faible</p>
              </div>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <TableauDonnees
            data={predictions}
            columns={columns}
            emptyMessage="Aucune prédiction disponible. Cliquez sur 'Générer les Prédictions' pour commencer."
          />
        </div>
      </div>
    </MiseEnPagePrincipale>
  )
}
