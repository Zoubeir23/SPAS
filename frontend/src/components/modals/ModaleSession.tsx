import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import Alerte from '@/components/common/Alerte'
import { sessionService } from '@/api/services/sessionService'

interface SessionModalProps {
  isOpen: boolean
  onClose: () => void
  sessionId?: string
  onSuccess?: () => void
}

export default function ModaleSession({
  isOpen,
  onClose,
  sessionId,
  onSuccess,
}: SessionModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    year: new Date().getFullYear().toString() + '-' + (new Date().getFullYear() + 1).toString(),
    startDate: '',
    endDate: '',
    status: 'active' as 'active' | 'inactive' | 'completed',
  })

  // Load session data if editing
  useEffect(() => {
    if (isOpen && sessionId) {
      const loadSession = async () => {
        try {
          const session = await sessionService.getById(sessionId)
          if (session) {
            setFormData({
              name: session.name || '',
              year: session.year || '',
              startDate: session.startDate || session.start_date || '',
              endDate: session.endDate || session.end_date || '',
              status: session.status || 'active',
            })
          }
        } catch (err) {
          console.error('Erreur lors du chargement de la session:', err)
        }
      }
      loadSession()
    } else if (isOpen && !sessionId) {
      // Reset form for new session
      const currentYear = new Date().getFullYear()
      setFormData({
        name: '',
        year: `${currentYear}-${currentYear + 1}`,
        startDate: '',
        endDate: '',
        status: 'active',
      })
      setError(null)
    }
  }, [isOpen, sessionId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name) {
      setError('Le nom de la session est requis')
      return
    }
    
    if (!formData.year) {
      setError('L\'année académique est requise')
      return
    }
    
    if (!formData.startDate) {
      setError('La date de début est requise')
      return
    }
    
    if (!formData.endDate) {
      setError('La date de fin est requise')
      return
    }
    
    if (new Date(formData.startDate) >= new Date(formData.endDate)) {
      setError('La date de fin doit être postérieure à la date de début')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      if (sessionId) {
        await sessionService.update(sessionId, formData)
      } else {
        await sessionService.create(formData)
      }
      onSuccess?.()
      onClose()
    } catch (err: any) {
      console.error('Erreur:', err)
      setError(
        err.response?.data?.detail || 
        err.response?.data?.message || 
        err.message || 
        'Une erreur est survenue lors de l\'enregistrement de la session'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title={sessionId ? 'Modifier la session' : 'Nouvelle session'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <Alerte type="error" onClose={() => setError(null)}>
            {error}
          </Alerte>
        )}

        <ChampSaisie
          label="Nom de la session"
          placeholder="Ex: Automne 2024"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <ChampSaisie
          label="Année académique"
          placeholder="Ex: 2024-2025"
          value={formData.year}
          onChange={(e) => setFormData({ ...formData, year: e.target.value })}
          required
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <ChampSaisie
            label="Date de début"
            type="date"
            value={formData.startDate}
            onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
            required
          />

          <ChampSaisie
            label="Date de fin"
            type="date"
            value={formData.endDate}
            onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2.5">
            Statut
          </label>
          <select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
            className="block w-full rounded-lg border border-gray-300 bg-white dark:bg-surface-dark py-3 px-4 text-sm text-gray-900 dark:text-white focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-700"
          >
            <option value="active">Actif</option>
            <option value="inactive">Inactif</option>
            <option value="completed">Terminé</option>
          </select>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Bouton
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={loading}
          >
            Annuler
          </Bouton>
          <Bouton
            type="submit"
            variant="primary"
            isLoading={loading}
            disabled={loading}
          >
            {sessionId ? 'Modifier' : 'Créer'}
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

