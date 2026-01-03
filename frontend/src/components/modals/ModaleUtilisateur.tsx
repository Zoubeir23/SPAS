import { useState, useEffect } from 'react'
import Modale from './Modale'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import { userService } from '@/api/services/userService'

interface UserModalProps {
  isOpen: boolean
  onClose: () => void
  userId?: string
  onSuccess?: () => void
}

export default function ModaleUtilisateur({ isOpen, onClose, userId, onSuccess }: UserModalProps) {
  const [loading, setLoading] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: 'teacher',
    password: '',
  })

  // Handle avatar upload
  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Check file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setError('La taille du fichier ne doit pas dépasser 2MB')
      return
    }

    // Check file type
    if (!file.type.startsWith('image/')) {
      setError('Seuls les fichiers image sont acceptés')
      return
    }

    setUploadingAvatar(true)
    try {
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      
      // Note: In a real implementation, you would upload to the server here
      // await userService.uploadAvatar(userId, file)
    } catch (err) {
      console.error('Erreur upload avatar:', err)
      setError('Erreur lors du téléchargement de la photo')
    } finally {
      setUploadingAvatar(false)
    }
  }

  // Handle avatar removal
  const handleAvatarRemove = () => {
    setAvatarPreview(null)
  }

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen && !userId) {
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        role: 'teacher',
        password: '',
      })
      setError(null)
    }
  }, [isOpen, userId])

  // Load user data if editing
  useEffect(() => {
    if (isOpen && userId) {
      userService.getById(userId).then(user => {
      setFormData({
        firstName: user.firstName || user.first_name || '',
        lastName: user.lastName || user.last_name || '',
        email: user.email,
        phone: '',
        role: user.role,
        password: '',
      })
      // Charger l'avatar si disponible
      if (user.avatar_url) {
        setAvatarPreview(user.avatar_url)
      }
      }).catch(err => {
        console.error('Erreur chargement utilisateur:', err)
        setError('Impossible de charger les données utilisateur')
      })
    }
  }, [isOpen, userId])

  const roles = [
    { id: 'admin', label: 'Administrateur', desc: 'Accès complet', icon: 'admin_panel_settings', color: 'blue' },
    { id: 'director', label: 'Direction Pédagogique', desc: 'Gestion des programmes', icon: 'school', color: 'purple' },
    { id: 'teacher', label: 'Enseignant', desc: 'Gestion des cours', icon: 'cast_for_education', color: 'green' },
    { id: 'data_scientist', label: 'Data Scientist', desc: 'Analytique & Prédictions', icon: 'science', color: 'orange' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      if (userId) {
        // Update existing user
        await userService.update(userId, {
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          role: formData.role as 'admin' | 'teacher' | 'ds' | 'pedagogical',
        })
      } else {
        // Create new user
        if (!formData.password) {
          setError('Le mot de passe est requis pour créer un utilisateur')
          setLoading(false)
          return
        }
        await userService.create({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName,
          role: formData.role,
        })
      }
      onSuccess?.()
      onClose()
    } catch (err) {
      console.error('Erreur:', err)
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modale isOpen={isOpen} onClose={onClose} title={userId ? "Modifier l'utilisateur" : "Ajouter un utilisateur"} size="xl">
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

        {/* Profile & Basic Info */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Profile Picture */}
          <div className="lg:col-span-4 flex flex-col items-center text-center space-y-4 pt-2">
            <div className="relative group">
              {avatarPreview ? (
                <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white dark:border-gray-800 shadow-lg">
                  <img
                    src={avatarPreview}
                    alt={`${formData.firstName} ${formData.lastName}`}
                    className="h-full w-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-32 h-32 rounded-full bg-gray-200 dark:bg-gray-700 border-4 border-white dark:border-gray-800 shadow-lg flex items-center justify-center">
                  <span className="material-symbols-outlined text-6xl text-gray-400">person</span>
                </div>
              )}
              <label
                className="absolute bottom-0 right-0 bg-primary text-white p-2 rounded-full shadow-md hover:bg-primary-dark transition-colors flex items-center justify-center w-9 h-9 border-2 border-white dark:border-gray-800 cursor-pointer"
                title="Changer la photo"
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarUpload}
                  className="hidden"
                  disabled={uploadingAvatar}
                />
                {uploadingAvatar ? (
                  <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                ) : (
                  <span className="material-symbols-outlined text-sm">edit</span>
                )}
              </label>
              {avatarPreview && (
                <button
                  type="button"
                  onClick={handleAvatarRemove}
                  className="absolute top-0 right-0 p-1.5 bg-red-500 text-white rounded-full shadow-md hover:bg-red-600 transition-colors text-xs"
                  title="Supprimer la photo"
                  disabled={uploadingAvatar}
                >
                  <span className="material-symbols-outlined text-sm">close</span>
                </button>
              )}
            </div>
            <div>
              <h4 className="text-gray-900 dark:text-white font-semibold text-lg">Photo de profil</h4>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Formats: JPG, PNG. Max 2MB.</p>
            </div>
          </div>

          {/* Basic Info Fields */}
          <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-5">
            <ChampSaisie
              required
              label="Prénom"
              placeholder="Ex: Thomas"
              value={formData.firstName}
              onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
            />
            <ChampSaisie
              required
              label="Nom"
              placeholder="Ex: Dubois"
              value={formData.lastName}
              onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
            />
            <div className="md:col-span-2">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  mail
                </span>
                <ChampSaisie
                  required
                  type="email"
                  label="Email"
                  className="pl-11"
                  placeholder="thomas.dubois@university.edu"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
            </div>
            <div className="md:col-span-2">
              <ChampSaisie
                type="tel"
                label="Téléphone"
                placeholder="+33 6 12 34 56 78"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
            {/* Password field - only for new users */}
            {!userId && (
              <div className="md:col-span-2">
                <ChampSaisie
                  required
                  type="password"
                  label="Mot de passe"
                  placeholder="Minimum 8 caractères"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
            )}
          </div>
        </div>

        <hr className="border-gray-200 dark:border-gray-800" />

        {/* Role Selection */}
        <div>
          <h3 className="text-gray-900 dark:text-white text-lg font-bold mb-4">Rôle et Permissions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {roles.map((role) => (
              <label key={role.id} className="relative group cursor-pointer">
                <input
                  type="radio"
                  name="role"
                  value={role.id}
                  checked={formData.role === role.id}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex flex-col items-center justify-center p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div className={`w-12 h-12 rounded-full ${
                    role.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' :
                    role.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400' :
                    role.color === 'green' ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' :
                    'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                  } flex items-center justify-center mb-3`}>
                    <span className="material-symbols-outlined">{role.icon}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900 dark:text-white text-center">
                    {role.label}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 text-center mt-1">
                    {role.desc}
                  </span>
                </div>
                <div className="absolute top-3 right-3 opacity-0 peer-checked:opacity-100 transition-opacity text-primary">
                  <span className="material-symbols-outlined">check_circle</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Bouton type="button" variant="outline" onClick={onClose}>
            Annuler
          </Bouton>
          <Bouton type="submit" disabled={loading}>
            <span className="material-symbols-outlined text-[20px] mr-2">save</span>
            {userId ? 'Modifier' : 'Créer'} l'utilisateur
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

