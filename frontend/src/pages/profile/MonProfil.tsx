import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import Carte from '@/components/common/Carte'
import Bouton from '@/components/common/Bouton'
import ChampSaisie from '@/components/common/ChampSaisie'
import { authService } from '@/api/services/authService'
import { userService } from '@/api/services/userService'
import { useAuthStore } from '@/store/authStore'

const roleLabels: Record<string, string> = {
  admin: 'Administrateur',
  teacher: 'Enseignant',
  ds: 'Data Scientist',
  pedagogical: 'Direction Pédagogique',
}

export default function MonProfil() {
  const { user: authUser, setUser } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [changingPassword, setChangingPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile')

  const [profileData, setProfileData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
  })
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)

  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  })

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    setLoading(true)
    setError(null)
    try {
      const user = await authService.getCurrentUser()
      setProfileData({
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: '', // Le téléphone n'est pas dans UserProfile, on le laisse vide pour l'instant
      })
      // Charger l'avatar si disponible
      if (user.avatar_url) {
        setAvatarPreview(user.avatar_url)
      } else if (authUser?.avatar_url) {
        setAvatarPreview(authUser.avatar_url)
      }
    } catch (err: any) {
      console.error('Erreur lors du chargement du profil:', err)
      setError('Impossible de charger votre profil')
    } finally {
      setLoading(false)
    }
  }

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validation du fichier
    if (!file.type.startsWith('image/')) {
      setError('Veuillez sélectionner un fichier image valide')
      return
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB max
      setError('L\'image ne doit pas dépasser 5 Mo')
      return
    }

    setUploadingAvatar(true)
    setError(null)
    setSuccessMessage(null)

    try {
      if (!authUser?.id) {
        throw new Error('ID utilisateur non disponible')
      }

      // Prévisualisation
      const reader = new FileReader()
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      // Upload
      const updatedUser = await userService.uploadAvatar(authUser.id, file)

      // Mettre à jour le store
      setUser({
        ...authUser,
        avatar: updatedUser.avatar,
        avatar_url: updatedUser.avatar_url,
      })

      setSuccessMessage('Photo de profil mise à jour avec succès')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err: any) {
      console.error('Erreur lors de l\'upload de l\'avatar:', err)
      setError(err.response?.data?.error || err.response?.data?.detail || 'Erreur lors de l\'upload de la photo')
      setAvatarPreview(null)
    } finally {
      setUploadingAvatar(false)
      // Réinitialiser l'input
      event.target.value = ''
    }
  }

  const handleAvatarRemove = async () => {
    if (!authUser?.id) return

    setUploadingAvatar(true)
    setError(null)
    setSuccessMessage(null)

    try {
      // Envoyer une requête pour supprimer l'avatar (mettre à null)
      await userService.update(authUser.id, { avatar: null as any })

      setUser({
        ...authUser,
        avatar: undefined,
        avatar_url: undefined,
      })

      setAvatarPreview(null)
      setSuccessMessage('Photo de profil supprimée avec succès')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err: any) {
      console.error('Erreur lors de la suppression de l\'avatar:', err)
      setError('Erreur lors de la suppression de la photo')
    } finally {
      setUploadingAvatar(false)
    }
  }

  const handleSaveProfile = async () => {
    setSaving(true)
    setError(null)
    setSuccessMessage(null)

    try {
      if (!authUser?.id) {
        throw new Error('ID utilisateur non disponible')
      }

      const updatedUser = await userService.update(authUser.id, {
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        email: profileData.email,
      })

      // Mettre à jour le store d'authentification
      setUser({
        ...authUser,
        firstName: updatedUser.firstName || updatedUser.first_name,
        lastName: updatedUser.lastName || updatedUser.last_name,
        email: updatedUser.email,
      })

      setSuccessMessage('Profil mis à jour avec succès')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err: any) {
      console.error('Erreur lors de la sauvegarde:', err)
      // Extraire le message d'erreur du backend
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.detail || 
                          err.response?.data?.message ||
                          err.message ||
                          'Erreur lors de la mise à jour du profil'
      setError(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    if (passwordData.new_password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères')
      return
    }

    setChangingPassword(true)
    setError(null)
    setSuccessMessage(null)

    try {
      if (!authUser?.id) {
        throw new Error('ID utilisateur non disponible')
      }

      await userService.changePassword(
        authUser.id,
        passwordData.old_password,
        passwordData.new_password
      )

      setSuccessMessage('Mot de passe modifié avec succès')
      setPasswordData({
        old_password: '',
        new_password: '',
        confirm_password: '',
      })
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err: any) {
      console.error('Erreur lors du changement de mot de passe:', err)
      // Extraire le message d'erreur du backend
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.detail || 
                          err.response?.data?.message ||
                          err.message ||
                          'Erreur lors du changement de mot de passe'
      setError(errorMessage)
    } finally {
      setChangingPassword(false)
    }
  }

  if (loading) {
    return (
      <MiseEnPagePrincipale title="Mon Profil">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Chargement du profil...</span>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  const displayName = authUser?.firstName && authUser?.lastName
    ? `${authUser.firstName} ${authUser.lastName}`
    : authUser?.email || 'Utilisateur'

  const initials = authUser?.firstName && authUser?.lastName
    ? `${authUser.firstName[0]}${authUser.lastName[0]}`
    : authUser?.email?.[0]?.toUpperCase() || 'U'

  return (
    <MiseEnPagePrincipale title="Mon Profil">
      <div className="mx-auto max-w-4xl flex flex-col gap-6">
        {/* Page Heading */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl font-black leading-tight tracking-tight text-gray-900 dark:text-white">
              Mon Profil
            </h1>
            <p className="text-base text-gray-500 dark:text-gray-400 leading-normal">
              Gérez vos informations personnelles et vos paramètres de compte
            </p>
          </div>
        </div>

        {/* Success/Error Messages */}
        {successMessage && (
          <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-green-700 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800">
            <span className="material-symbols-outlined mr-2 align-middle">check_circle</span>
            {successMessage}
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800">
            <span className="material-symbols-outlined mr-2 align-middle">error</span>
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-800">
          <div className="flex gap-8 overflow-x-auto">
            <button
              onClick={() => setActiveTab('profile')}
              className={`group flex flex-col items-center justify-center border-b-[3px] pb-[13px] pt-4 min-w-fit transition-colors ${
                activeTab === 'profile'
                  ? 'border-primary text-gray-900 dark:text-white'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-gray-200'
              }`}
            >
              <p className="text-sm font-bold leading-normal tracking-[0.015em]">Informations Personnelles</p>
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`group flex flex-col items-center justify-center border-b-[3px] pb-[13px] pt-4 min-w-fit transition-colors ${
                activeTab === 'password'
                  ? 'border-primary text-gray-900 dark:text-white'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-gray-200'
              }`}
            >
              <p className="text-sm font-bold leading-normal tracking-[0.015em]">Sécurité</p>
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'profile' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Profile Picture */}
            <div className="lg:col-span-1">
              <Carte>
                <div className="flex flex-col items-center text-center">
                  <div className="relative mb-4">
                    {avatarPreview ? (
                      <div className="h-32 w-32 rounded-full overflow-hidden border-4 border-white dark:border-gray-700 shadow-lg">
                        <img
                          src={avatarPreview}
                          alt={displayName}
                          className="h-full w-full object-cover"
                        />
                      </div>
                    ) : (
                      <div className="h-32 w-32 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-bold text-3xl shadow-lg">
                        {initials}
                      </div>
                    )}
                    <label
                      className="absolute bottom-0 right-0 p-2 bg-white dark:bg-gray-800 rounded-full shadow-md hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700 cursor-pointer"
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
                        <span className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full inline-block"></span>
                      ) : (
                        <span className="material-symbols-outlined text-gray-600 dark:text-gray-400 text-lg">
                          camera_alt
                        </span>
                      )}
                    </label>
                    {avatarPreview && (
                      <button
                        onClick={handleAvatarRemove}
                        className="absolute top-0 right-0 p-1.5 bg-red-500 text-white rounded-full shadow-md hover:bg-red-600 transition-colors text-xs"
                        title="Supprimer la photo"
                        disabled={uploadingAvatar}
                      >
                        <span className="material-symbols-outlined text-sm">close</span>
                      </button>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                    {displayName}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    {authUser?.email}
                  </p>
                  <div className="inline-flex items-center px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                    {roleLabels[authUser?.role || ''] || authUser?.role || 'Utilisateur'}
                  </div>
                </div>
              </Carte>
            </div>

            {/* Right Column: Profile Form */}
            <div className="lg:col-span-2">
              <Carte>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-bold leading-tight text-gray-900 dark:text-white">
                      Informations Personnelles
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      Mettez à jour vos informations de profil
                    </p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Prénom <span className="text-red-600">*</span>
                      </label>
                      <ChampSaisie
                        type="text"
                        value={profileData.first_name}
                        onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })}
                        placeholder="Votre prénom"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Nom <span className="text-red-600">*</span>
                      </label>
                      <ChampSaisie
                        type="text"
                        value={profileData.last_name}
                        onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })}
                        placeholder="Votre nom"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email <span className="text-red-600">*</span>
                    </label>
                    <div className="relative">
                      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <span className="material-symbols-outlined text-gray-400 text-[20px]">mail</span>
                      </div>
                      <ChampSaisie
                        type="email"
                        className="pl-10"
                        value={profileData.email}
                        onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                        placeholder="votre.email@example.com"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Téléphone
                    </label>
                    <div className="relative">
                      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <span className="material-symbols-outlined text-gray-400 text-[20px]">call</span>
                      </div>
                      <ChampSaisie
                        type="tel"
                        className="pl-10"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                        placeholder="+221 77 123 45 67"
                      />
                    </div>
                  </div>

                  <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <Bouton onClick={handleSaveProfile} disabled={saving}>
                      {saving ? (
                        <>
                          <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                          Enregistrement...
                        </>
                      ) : (
                        <>
                          <span className="material-symbols-outlined text-sm mr-1">save</span>
                          Enregistrer les modifications
                        </>
                      )}
                    </Bouton>
                  </div>
                </div>
              </Carte>
            </div>
          </div>
        )}

        {activeTab === 'password' && (
          <Carte>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold leading-tight text-gray-900 dark:text-white">
                  Changer le mot de passe
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Mettez à jour votre mot de passe pour sécuriser votre compte
                </p>
              </div>
              <span className="material-symbols-outlined text-gray-400">lock</span>
            </div>

            <div className="space-y-6 max-w-2xl">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Mot de passe actuel <span className="text-red-600">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                    <span className="material-symbols-outlined text-gray-400 text-[20px]">lock</span>
                  </div>
                  <ChampSaisie
                    type="password"
                    className="pl-10"
                    value={passwordData.old_password}
                    onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                    placeholder="Entrez votre mot de passe actuel"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nouveau mot de passe <span className="text-red-600">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                    <span className="material-symbols-outlined text-gray-400 text-[20px]">lock_reset</span>
                  </div>
                  <ChampSaisie
                    type="password"
                    className="pl-10"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                    placeholder="Minimum 8 caractères"
                    required
                  />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Le mot de passe doit contenir au moins 8 caractères
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Confirmer le nouveau mot de passe <span className="text-red-600">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                    <span className="material-symbols-outlined text-gray-400 text-[20px]">lock_reset</span>
                  </div>
                  <ChampSaisie
                    type="password"
                    className="pl-10"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    placeholder="Confirmez votre nouveau mot de passe"
                    required
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <Bouton onClick={handleChangePassword} disabled={changingPassword}>
                  {changingPassword ? (
                    <>
                      <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                      Modification...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-sm mr-1">lock</span>
                      Changer le mot de passe
                    </>
                  )}
                </Bouton>
              </div>
            </div>
          </Carte>
        )}
      </div>
    </MiseEnPagePrincipale>
  )
}

