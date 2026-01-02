import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import { mlService } from '@/api/services/mlService'

interface TrainingModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function ModaleEntrainement({ isOpen, onClose, onSuccess }: TrainingModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [trainingProgress, setTrainingProgress] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    algorithm: 'random_forest',
    dateRange: { start: '', end: '' },
    features: [] as string[],
    hyperparameters: {} as Record<string, number | boolean>,
    description: '',
  })

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        algorithm: 'random_forest',
        dateRange: { start: '', end: '' },
        features: [],
        hyperparameters: {},
        description: '',
      })
      setError(null)
      setTrainingProgress(null)
    }
  }, [isOpen])

  const algorithms = [
    { id: 'random_forest', label: 'Random Forest', desc: 'Robuste, interprétable' },
    { id: 'xgboost', label: 'XGBoost', desc: 'Haute performance' },
    { id: 'neural_network', label: 'Réseau de Neurones', desc: 'Complexe, puissant' },
    { id: 'svm', label: 'SVM', desc: 'Classification précise' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setTrainingProgress('Création du modèle...')
    
    try {
      // Step 1: Create the model
      const modelName = formData.name || `Modèle ${formData.algorithm} - ${new Date().toLocaleDateString('fr-FR')}`
      const newModel = await mlService.trainModel({
        name: modelName,
        description: formData.description || `Algorithme: ${formData.algorithm}`,
      })
      
      setTrainingProgress('Démarrage de l\'entraînement...')
      
      // Step 2: Start training
      await mlService.startTraining(newModel.id)
      
      setTrainingProgress('Entraînement terminé avec succès!')
      
      // Wait a bit to show success message
      await new Promise((resolve) => setTimeout(resolve, 1000))
      
      onSuccess?.()
      onClose()
    } catch (err) {
      console.error('Erreur:', err)
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'entraînement du modèle')
    } finally {
      setLoading(false)
      setTrainingProgress(null)
    }
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title="Nouvel Entraînement" size="lg">
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
              <span className="material-symbols-outlined text-lg">error</span>
              {error}
            </p>
          </div>
        )}

        {/* Training Progress */}
        {trainingProgress && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-600 dark:text-blue-400 flex items-center gap-2">
              <span className="material-symbols-outlined text-lg animate-spin">sync</span>
              {trainingProgress}
            </p>
          </div>
        )}

        {/* Configuration Section */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-primary text-xl">tune</span>
            <h4 className="text-base font-semibold text-gray-900 dark:text-white">
              Configuration de l'Entraînement
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-300">
                Nom du modèle
              </label>
              <ChampSaisie
                required
                placeholder="Ex: Modèle Prédictif v2.5"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-900 dark:text-gray-300">
                Période des données
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-gray-400 text-[18px]">
                    calendar_month
                  </span>
                </div>
                <ChampSaisie
                  type="date"
                  className="pl-10"
                  value={formData.dateRange.start}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      dateRange: { ...formData.dateRange, start: e.target.value },
                    })
                  }
                />
              </div>
            </div>
          </div>
        </section>

        {/* Algorithm Selection */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-primary text-xl">psychology</span>
            <h4 className="text-base font-semibold text-gray-900 dark:text-white">
              Algorithme d'Apprentissage
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {algorithms.map((algo) => (
              <label key={algo.id} className="relative group cursor-pointer">
                <input
                  type="radio"
                  name="algorithm"
                  value={algo.id}
                  checked={formData.algorithm === algo.id}
                  onChange={(e) => setFormData({ ...formData, algorithm: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex flex-col p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-gray-900 dark:text-white">
                      {algo.label}
                    </span>
                    {formData.algorithm === algo.id && (
                      <span className="material-symbols-outlined text-primary">check_circle</span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{algo.desc}</span>
                </div>
              </label>
            ))}
          </div>
        </section>

        {/* Advanced Options */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-primary text-xl">tune</span>
            <h4 className="text-base font-semibold text-gray-900 dark:text-white">
              Options Avancées
            </h4>
          </div>

          <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">
                  Validation croisée
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Utiliser la validation croisée 5-fold
                </p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">
                  Recherche hyperparamètres
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Recherche automatique des meilleurs paramètres
                </p>
              </div>
              <input type="checkbox" className="rounded" />
            </label>
          </div>
        </section>

        {/* Footer */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Bouton type="button" variant="outline" onClick={onClose}>
            Annuler
          </Bouton>
          <Bouton type="submit" disabled={loading}>
            <span className="material-symbols-outlined text-[20px] mr-2">play_arrow</span>
            {loading ? 'Lancement...' : 'Lancer l\'entraînement'}
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

