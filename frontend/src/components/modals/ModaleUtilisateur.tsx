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
    password_confirm: '',
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
        password_confirm: '',
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
        password_confirm: '',
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
    { id: 'pedagogical', label: 'Direction Pédagogique', desc: 'Gestion des programmes', icon: 'school', color: 'purple' },
    { id: 'teacher', label: 'Enseignant', desc: 'Gestion des cours', icon: 'cast_for_education', color: 'green' },
    { id: 'ds', label: 'Data Scientist', desc: 'Analytique & Prédictions', icon: 'science', color: 'orange' },
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
        if (formData.password !== formData.password_confirm) {
          setError('Les mots de passe ne correspondent pas')
          setLoading(false)
          return
        }
        await userService.create({
          email: formData.email,
          password: formData.password,
          password_confirm: formData.password_confirm,
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
    <Modale isOpen={isOpen} onClose={onClose} title={userId ? "Modifier l'utilisateur" : "Nouvel utilisateur"} size="xl">
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

        {/* Profile & Basic Info */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Picture */}
          <div className="lg:col-span-1 flex flex-col items-center text-center space-y-4 pt-2">
            <div className="relative group">
              {avatarPreview ? (
                <div className="w-28 h-28 rounded-full overflow-hidden border-4 border-primary/20 shadow-lg ring-4 ring-white dark:ring-gray-800">
                  <img
                    src={avatarPreview}
                    alt={`${formData.firstName} ${formData.lastName}`}
                    className="h-full w-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-28 h-28 rounded-full bg-gradient-to-br from-primary/10 to-primary/5 border-4 border-primary/20 shadow-lg flex items-center justify-center">
                  <span className="material-symbols-outlined text-5xl text-primary/40">person</span>
                </div>
              )}
              <label
                className="absolute bottom-1 right-1 bg-primary text-white p-2 rounded-full shadow-lg hover:bg-primary-dark transition-all flex items-center justify-center w-8 h-8 border-2 border-white dark:border-gray-800 cursor-pointer hover:scale-110"
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
                  <span className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full"></span>
                ) : (
                  <span className="material-symbols-outlined text-sm">photo_camera</span>
                )}
              </label>
              {avatarPreview && (
                <button
                  type="button"
                  onClick={handleAvatarRemove}
                  className="absolute -top-1 -right-1 p-1 bg-red-500 text-white rounded-full shadow-md hover:bg-red-600 transition-all hover:scale-110"
                  title="Supprimer la photo"
                  disabled={uploadingAvatar}
                >
                  <span className="material-symbols-outlined text-xs">close</span>
                </button>
              )}
            </div>
            <div>
              <h4 className="text-gray-900 dark:text-white font-semibold">Photo de profil</h4>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">JPG, PNG. Max 2MB</p>
            </div>
          </div>

          {/* Basic Info Fields */}
          <div className="lg:col-span-2 space-y-5">
            {/* Nom et Prénom sur la même ligne */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <ChampSaisie
                required
                label="Prénom"
                leftIcon="person"
                placeholder="Thomas"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
              />
              <ChampSaisie
                required
                label="Nom"
                leftIcon="badge"
                placeholder="Dubois"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
              />
            </div>
            
            {/* Email */}
            <ChampSaisie
              required
              type="email"
              label="Email"
              leftIcon="mail"
              placeholder="thomas.dubois@university.edu"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
            
            {/* Téléphone */}
            <ChampSaisie
              type="tel"
              label="Téléphone"
              leftIcon="phone"
              placeholder="+221 78 123 45 67"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
            
            {/* Password fields - only for new users */}
            {!userId && (
              <>
                <ChampSaisie
                  required
                  type="password"
                  label="Mot de passe"
                  leftIcon="lock"
                  placeholder="Minimum 8 caractères"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
                <ChampSaisie
                  required
                  type="password"
                  label="Confirmer le mot de passe"
                  leftIcon="lock"
                  placeholder="Répétez le mot de passe"
                  value={formData.password_confirm}
                  onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })}
                />
              </>
            )}
          </div>
        </div>

        <hr className="border-gray-200 dark:border-gray-700" />

        {/* Role Selection */}
        <div>
          <h3 className="text-gray-900 dark:text-white text-base font-bold mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">security</span>
            Rôle et Permissions
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {roles.map((role) => (
              <label key={role.id} className="relative cursor-pointer">
                <input
                  type="radio"
                  name="role"
                  value={role.id}
                  checked={formData.role === role.id}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="peer sr-only"
                />
                <div className="flex flex-col items-center justify-center p-3 rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div className={`w-10 h-10 rounded-full ${
                    role.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' :
                    role.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400' :
                    role.color === 'green' ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' :
                    'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                  } flex items-center justify-center mb-2`}>
                    <span className="material-symbols-outlined text-xl">{role.icon}</span>
                  </div>
                  <span className="text-xs font-bold text-gray-900 dark:text-white text-center leading-tight">
                    {role.label}
                  </span>
                  <span className="text-[10px] text-gray-500 dark:text-gray-400 text-center mt-0.5">
                    {role.desc}
                  </span>
                </div>
                <div className="absolute top-2 right-2 opacity-0 peer-checked:opacity-100 transition-opacity text-primary">
                  <span className="material-symbols-outlined text-lg">check_circle</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 pt-5 border-t border-gray-200 dark:border-gray-700">
          <Bouton type="button" variant="outline" onClick={onClose}>
            Annuler
          </Bouton>
          <Bouton type="submit" disabled={loading}>
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                {userId ? 'Modification...' : 'Création...'}
              </span>
            ) : (
              <>
                <span className="material-symbols-outlined text-lg mr-1.5">{userId ? 'save' : 'person_add'}</span>
                {userId ? 'Enregistrer' : 'Créer'}
              </>
            )}
          </Bouton>
        </div>
      </form>
    </Modale>
  )
}

