import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import BarreRecherche from '@/components/common/BarreRecherche'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import ModaleUtilisateur from '@/components/modals/ModaleUtilisateur'
import ModaleConfirmation from '@/components/common/ModaleConfirmation'
import { userService, User } from '@/api/services/userService'
import { useAuthStore } from '@/store/authStore'
import { toast } from 'react-toastify'

const roleLabels: Record<string, string> = {
  admin: 'Administrateur',
  teacher: 'Enseignant',
  ds: 'Data Scientist',
  pedagogical: 'Direction Pédagogique',
}

export default function GestionUtilisateurs() {
  const { user: currentUser } = useAuthStore()
  const isAdmin = currentUser?.role === 'admin'
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('all')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; user: User | null }>({
    isOpen: false,
    user: null,
  })

  const loadUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await userService.getAll()
      setUsers(response.results)
      setFilteredUsers(response.results)
    } catch (err) {
      console.error('Erreur lors du chargement des utilisateurs:', err)
      setError('Impossible de charger les utilisateurs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  useEffect(() => {
    let filtered = users

    if (searchQuery) {
      filtered = filtered.filter(
        (u) =>
          (u.firstName || u.first_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (u.lastName || u.last_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.email.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (selectedRole !== 'all') {
      filtered = filtered.filter((u) => u.role === selectedRole)
    }

    setFilteredUsers(filtered)
  }, [searchQuery, selectedRole, users])

  const handleUserCreated = async () => {
    // Recharger la liste des utilisateurs depuis l'API
    await loadUsers()
    setIsModalOpen(false)
    setEditingUser(null)
  }

  const handleDeleteUser = (user: User) => {
    setDeleteConfirmation({ isOpen: true, user })
  }

  const confirmDeleteUser = async () => {
    if (deleteConfirmation.user) {
      try {
        await userService.delete(deleteConfirmation.user.id)
        await loadUsers()
        toast.success('Utilisateur supprimé avec succès')
      } catch (err) {
        console.error('Erreur lors de la suppression:', err)
        toast.error('Erreur lors de la suppression de l\'utilisateur')
      }
    }
  }

  const columns: Column<User>[] = [
    {
      key: 'name',
      label: 'Utilisateur',
      render: (user) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
            {(user.firstName || user.first_name || '?')[0]}
            {(user.lastName || user.last_name || '?')[0]}
          </div>
          <div>
            <div className="text-sm font-semibold text-gray-900 dark:text-white">
              {user.firstName || user.first_name} {user.lastName || user.last_name}
            </div>
            <div className="text-xs text-gray-500">{user.email}</div>
          </div>
        </div>
      ),
      sortable: true,
    },
    {
      key: 'role',
      label: 'Rôle',
      render: (user) => (
        <Badge variant="info">{roleLabels[user.role] || user.role}</Badge>
      ),
      sortable: true,
    },
    {
      key: 'status',
      label: 'Statut',
      render: (user) => (
        <Badge variant={(user.is_active ?? user.isActive) ? 'success' : 'warning'}>
          {(user.is_active ?? user.isActive) ? 'Actif' : 'Inactif'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      label: 'Date de création',
      render: (user) => user.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : '-',
      sortable: true,
    },
  ]

  const handleActions = (user: User) => {
    // Seul l'admin peut modifier/supprimer des utilisateurs
    if (!isAdmin) {
      return <span className="text-gray-400 text-sm">Aucune action disponible</span>
    }
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={() => {
            setEditingUser(user)
            setIsModalOpen(true)
          }}
          className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title="Modifier"
        >
          <span className="material-symbols-outlined text-[20px]">edit</span>
        </button>
        <button
          onClick={() => handleDeleteUser(user)}
          className="text-gray-400 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title="Supprimer"
        >
          <span className="material-symbols-outlined text-[20px]">delete</span>
        </button>
      </div>
    )
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

  if (error) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <div className="text-red-500 dark:text-red-400">{error}</div>
          <button
            onClick={loadUsers}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
          >
            Réessayer
          </button>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  return (
    <MiseEnPagePrincipale title="Gestion des Utilisateurs">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Page Heading */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl md:text-4xl font-black tracking-tight text-gray-900 dark:text-white">
              Gestion des Utilisateurs
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-base max-w-2xl">
              Gérez les accès et les rôles pour le personnel, les enseignants et l'administration
              de l'ISI.
            </p>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between bg-white dark:bg-surface-dark p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex flex-col sm:flex-row gap-3 flex-1">
            <div className="relative flex-1 min-w-[240px]">
              <BarreRecherche
                placeholder="Rechercher par nom ou email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <div className="relative min-w-[160px]">
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full pl-10 pr-8 py-2.5 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm text-gray-900 dark:text-white appearance-none cursor-pointer focus:ring-2 focus:ring-primary/50"
              >
                <option value="all">Tous les rôles</option>
                <option value="admin">Administrateur</option>
                <option value="teacher">Enseignant</option>
                <option value="ds">Data Scientist</option>
                <option value="pedagogical">Direction Pédagogique</option>
              </select>
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 material-symbols-outlined text-[20px]">
                filter_list
              </span>
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 material-symbols-outlined text-[16px] pointer-events-none">
                expand_more
              </span>
            </div>
          </div>
          {isAdmin && (
            <Bouton onClick={() => { setEditingUser(null); setIsModalOpen(true); }}>
              <span className="material-symbols-outlined text-[20px]">add</span>
              Nouvel utilisateur
            </Bouton>
          )}
        </div>

        {/* Data Table */}
        <TableauDonnees
          data={filteredUsers}
          columns={columns}
          actions={handleActions}
          emptyMessage="Aucun utilisateur trouvé"
        />

        {/* User Modal */}
        <ModaleUtilisateur
          isOpen={isModalOpen}
          onClose={() => { setIsModalOpen(false); setEditingUser(null); }}
          onSuccess={handleUserCreated}
          userId={editingUser?.id}
        />

        <ModaleConfirmation
          isOpen={deleteConfirmation.isOpen}
          onClose={() => setDeleteConfirmation({ isOpen: false, user: null })}
          onConfirm={confirmDeleteUser}
          title="Supprimer l'utilisateur"
          message={`Êtes-vous sûr de vouloir supprimer ${deleteConfirmation.user ? (deleteConfirmation.user.firstName || deleteConfirmation.user.first_name) + ' ' + (deleteConfirmation.user.lastName || deleteConfirmation.user.last_name) : 'cet utilisateur'} ? Cette action est irréversible.`}
          confirmText="Supprimer"
          cancelText="Annuler"
          variant="danger"
        />
      </div>
    </MiseEnPagePrincipale>
  )
}
