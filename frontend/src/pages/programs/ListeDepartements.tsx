import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import { departmentService, Department } from '@/api/services/programService'

export default function ListeDepartements() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadDepartments = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await departmentService.getAll()
        setDepartments(data)
      } catch (err) {
        console.error('Erreur lors du chargement des départements:', err)
        setError('Impossible de charger les départements')
      } finally {
        setLoading(false)
      }
    }
    loadDepartments()
  }, [])

  const columns: Column<Department>[] = [
    {
      key: 'code',
      label: 'Code',
      sortable: true,
    },
    {
      key: 'name',
      label: 'Nom',
      sortable: true,
    },
    {
      key: 'program_count',
      label: 'Filières',
      render: (dept) => dept.program_count || 0,
      sortable: true,
    },
    {
      key: 'status',
      label: 'Statut',
      render: (dept) => (
        <Badge variant={dept.status === 'active' ? 'success' : 'warning'}>
          {dept.status === 'active' ? 'Actif' : 'Inactif'}
        </Badge>
      ),
    },
  ]

  if (loading) {
    return (
      <MiseEnPagePrincipale>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Chargement...</span>
        </div>
      </MiseEnPagePrincipale>
    )
  }

  return (
    <MiseEnPagePrincipale title="Liste des Départements">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Liste des Départements
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Gérez les départements académiques de l'établissement.
            </p>
          </div>
          <Bouton>Nouveau département</Bouton>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        <TableauDonnees 
          data={departments} 
          columns={columns} 
          emptyMessage="Aucun département trouvé" 
        />
      </div>
    </MiseEnPagePrincipale>
  )
}
