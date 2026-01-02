import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import { interventionService } from '@/api/services/interventionService'

interface InterventionModalProps {
  isOpen: boolean
  onClose: () => void
  studentId?: string
  studentName?: string
  onSuccess?: () => void
}

export default function ModaleIntervention({
  isOpen,
  onClose,
  studentId,
  studentName,
  onSuccess,
}: InterventionModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    type: 'meeting',
    date: new Date().toISOString().split('T')[0],
    description: '',
    priority: 'medium',
  })

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        type: 'meeting',
        date: new Date().toISOString().split('T')[0],
        description: '',
        priority: 'medium',
      })
      setError(null)
    }
  }, [isOpen])

  const interventionTypes = [
    { id: 'meeting', label: 'Entretien individuel', icon: 'person', color: 'purple' },
    { id: 'tutoring', label: 'Tutorat', icon: 'school', color: 'blue' },
    { id: 'alert', label: 'Alerte précoce', icon: 'notifications', color: 'orange' },
    { id: 'email', label: 'Email de suivi', icon: 'mail', color: 'green' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!studentId) {
      setError('Aucun étudiant sélectionné')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      await interventionService.create({
        student: studentId,
        type: formData.type,
        priority: formData.priority,
        description: formData.description || `Intervention ${formData.type} pour ${studentName || 'étudiant'}`,
        scheduled_date: formData.date,
      })
      onSuccess?.()
      onClose()
    } catch (err) {
      console.error('Erreur:', err)
      setError(err instanceof Error ? err.message : 'Une erreur est survenue lors de la création de l\'intervention')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title="Nouvelle Intervention Pédagogique" size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
              <span className="material-symbols-outlined text-lg">error</span>
              {error}
            </p>
          </div>
        )}

        {studentName && (
          <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Intervention pour : <span className="font-semibold text-gray-900 dark:text-white">{studentName}</span>
            </p>
          </div>
        )}

        {/* Intervention Type */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-4">
            Type d'intervention <span className="text-red-600">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {interventionTypes.map((type) => (
              <label key={type.id} className="relative group cursor-pointer">
                <input
                  type="radio"
                  name="interventionType"
                  value={type.id}
                  checked={formData.type === type.id}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex items-center gap-3 p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all">
                  <div className={`p-2 rounded-lg ${
                    type.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600' :
                    type.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600' :
                    type.color === 'orange' ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600' :
                    'bg-green-100 dark:bg-green-900/30 text-green-600'
                  }`}>
                    <span className="material-symbols-outlined">{type.icon}</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                    {type.label}
                  </span>
                  {formData.type === type.id && (
                    <span className="ml-auto material-symbols-outlined text-primary">
                      check_circle
                    </span>
                  )}
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Date */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Date prévue <span className="text-red-600">*</span>
          </label>
          <ChampSaisie
            required
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          />
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Priorité
          </label>
          <select
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-2.5 pl-3 pr-10 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm"
          >
            <option value="low">Faible</option>
            <option value="medium">Moyenne</option>
            <option value="high">Élevée</option>
            <option value="urgent">Urgente</option>
          </select>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Description / Notes
          </label>
          <textarea
            className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 py-2.5 px-3 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-gray-800 sm:text-sm resize-none"
            rows={4}
            placeholder="Décrivez l'intervention prévue..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Bouton type="button" variant="outline" onClick={onClose}>
            Annuler
          </Bouton>
          <Bouton type="submit" disabled={loading}>
            <span className="material-symbols-outlined text-[20px] mr-2">save</span>
            Enregistrer l'intervention
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

