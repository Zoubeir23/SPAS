import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import { programService } from '@/api/services/programService'
import { toast } from 'react-toastify'

interface ModaleFiliereProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  programId?: string
}

interface FormData {
  code: string
  name: string
  description: string
  duration: number
  status: 'active' | 'inactive'
}

interface FormErrors {
  code?: string
  name?: string
  description?: string
  duration?: string
  status?: string
}

export default function ModaleFiliere({
  isOpen,
  onClose,
  onSuccess,
  programId
}: ModaleFiliereProps) {
  const [formData, setFormData] = useState<FormData>({
    code: '',
    name: '',
    description: '',
    duration: 3,
    status: 'active'
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})

  const isEditMode = !!programId

  useEffect(() => {
    if (isOpen && programId) {
      const loadProgram = async () => {
        try {
          const program = await programService.getById(programId)
          if (program) {
            setFormData({
              code: program.code || '',
              name: program.name || '',
              description: program.description || '',
              duration: program.duration || 3,
              status: program.status || 'active'
            })
          }
        } catch (error) {
          console.error('Erreur chargement filière:', error)
          toast.error('Erreur lors du chargement de la filière')
        }
      }
      loadProgram()
    } else if (isOpen) {
      // Reset form pour nouvelle filière
      setFormData({
        code: '',
        name: '',
        description: '',
        duration: 3,
        status: 'active'
      })
      setErrors({})
    }
  }, [isOpen, programId])

  const validate = (): boolean => {
    const newErrors: FormErrors = {}
    if (!formData.code.trim()) {
      newErrors.code = 'Le code est requis'
    }
    if (!formData.name.trim()) {
      newErrors.name = 'Le nom est requis'
    }
    if (formData.duration < 1 || formData.duration > 10) {
      newErrors.duration = 'La durée doit être entre 1 et 10 ans'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      if (isEditMode && programId) {
        await programService.update(programId, formData)
        toast.success('Filière mise à jour avec succès')
      } else {
        await programService.create(formData)
        toast.success('Filière créée avec succès')
      }
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Erreur:', error)
      toast.error(isEditMode ? 'Erreur lors de la mise à jour' : 'Erreur lors de la création')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modale
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? 'Modifier la filière' : 'Nouvelle filière'}
      size="md"
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ChampSaisie
            label="Code"
            placeholder="Ex: GL, RI, DSBD"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
            error={errors.code}
            required
          />
          <ChampSaisie
            label="Durée (années)"
            type="number"
            min={1}
            max={10}
            value={String(formData.duration)}
            onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || 1 })}
            error={errors.duration}
            required
          />
        </div>

        <ChampSaisie
          label="Nom de la filière"
          placeholder="Ex: Génie Logiciel, Cyber Sécurité, Data Science & Big Data Technology"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          error={errors.name}
          required
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Description
          </label>
          <textarea
            rows={3}
            placeholder="Description de la filière..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Bouton variant="outline" type="button" onClick={onClose}>
            Annuler
          </Bouton>
          <Bouton type="submit" disabled={loading}>
            {loading ? 'Enregistrement...' : isEditMode ? 'Mettre à jour' : 'Créer la filière'}
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}
