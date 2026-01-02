import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import BarreRecherche from '@/components/common/BarreRecherche'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import ModaleUtilisateur from '@/components/modals/ModaleUtilisateur'

interface User {
  id: string
  firstName: string
  lastName: string
  email: string
  role: 'admin' | 'teacher' | 'ds' | 'pedagogical'
  status: 'active' | 'inactive'
  createdAt: string
}

// Mock data
const mockUsers: User[] = [
  {
    id: '1',
    firstName: 'Sophie',
    lastName: 'Martin',
    email: 'sophie.martin@isi.edu',
    role: 'admin',
    status: 'active',
    createdAt: '2023-01-15',
  },
  {
    id: '2',
    firstName: 'Pierre',
    lastName: 'Dupont',
    email: 'pierre.dupont@isi.edu',
    role: 'teacher',
    status: 'active',
    createdAt: '2023-02-20',
  },
  {
    id: '3',
    firstName: 'Marie',
    lastName: 'Sarr',
    email: 'marie.sarr@isi.edu',
    role: 'ds',
    status: 'active',
    createdAt: '2023-03-10',
  },
]

const roleLabels: Record<string, string> = {
  admin: 'Administrateur',
  teacher: 'Enseignant',
  ds: 'Data Scientist',
  pedagogical: 'Direction Pédagogique',
}

export default function GestionUtilisateurs() {
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('all')
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true)
      await new Promise((resolve) => setTimeout(resolve, 500))
      setUsers(mockUsers)
      setFilteredUsers(mockUsers)
      setLoading(false)
    }
    loadUsers()
  }, [])

  useEffect(() => {
    let filtered = users

    if (searchQuery) {
      filtered = filtered.filter(
        (u) =>
          u.firstName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.lastName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          u.email.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (selectedRole !== 'all') {
      filtered = filtered.filter((u) => u.role === selectedRole)
    }

    setFilteredUsers(filtered)
  }, [searchQuery, selectedRole, users])

  const handleUserCreated = async () => {
    // Recharger la liste des utilisateurs
    setLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 500))
    // En production, faire un vrai appel API ici
    setLoading(false)
  }

  const columns: Column<User>[] = [
    {
      key: 'name',
      label: 'Utilisateur',
      render: (user) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
            {user.firstName[0]}
            {user.lastName[0]}
          </div>
          <div>
            <div className="text-sm font-semibold text-gray-900 dark:text-white">
              {user.firstName} {user.lastName}
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
        <Badge variant={user.status === 'active' ? 'success' : 'warning'}>
          {user.status === 'active' ? 'Actif' : 'Inactif'}
        </Badge>
      ),
    },
    {
      key: 'createdAt',
      label: 'Date de création',
      render: (user) => new Date(user.createdAt).toLocaleDateString('fr-FR'),
      sortable: true,
    },
  ]

  const handleActions = (_user: User) => (
    <div className="flex items-center gap-2">
      <button
        onClick={() => {
          // TODO: Ouvrir modale d'édition
        }}
        className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="Modifier"
      >
        <span className="material-symbols-outlined text-[20px]">edit</span>
      </button>
      <button
        onClick={() => {
          // TODO: Supprimer
        }}
        className="text-gray-400 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="Supprimer"
      >
        <span className="material-symbols-outlined text-[20px]">delete</span>
      </button>
    </div>
  )

  if (loading) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500 dark:text-gray-400">Chargement...</div>
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
          <Bouton onClick={() => setIsModalOpen(true)}>
            <span className="material-symbols-outlined text-[20px]">add</span>
            Nouvel utilisateur
          </Bouton>
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
          onClose={() => setIsModalOpen(false)}
          onSuccess={handleUserCreated}
        />
      </div>
    </MiseEnPagePrincipale>
  )
}
