import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import ModaleFiliere from '@/components/modals/ModaleFiliere'
import { programService, Program } from '@/api/services/programService'

export default function ListeFilieres() {
  const [programs, setPrograms] = useState<Program[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedProgramId, setSelectedProgramId] = useState<string | undefined>(undefined)

  const loadPrograms = async () => {
    setLoading(true)
    try {
      const data = await programService.getAll()
      setPrograms(data)
    } catch (error) {
      console.error('Erreur lors du chargement des filières:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPrograms()
  }, [])

  const columns: Column<Program>[] = [
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
      key: 'duration',
      label: 'Durée (années)',
      sortable: true,
    },
    {
      key: 'studentCount',
      label: 'Étudiants',
      render: (program) => program.studentCount || 0,
      sortable: true,
    },
    {
      key: 'status',
      label: 'Statut',
      render: (program) => (
        <Badge variant={program.status === 'active' ? 'success' : 'warning'}>
          {program.status}
        </Badge>
      ),
    },
  ]

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
    <MiseEnPagePrincipale title="Liste des Filières">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Liste des Filières
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Gérez les filières et programmes académiques.
            </p>
          </div>
          <Bouton onClick={() => { setSelectedProgramId(undefined); setIsModalOpen(true); }}>Nouvelle filière</Bouton>
        </div>

        <TableauDonnees 
          data={programs} 
          columns={columns} 
          emptyMessage="Aucune filière trouvée"
          actions={(program) => (
            <button
              onClick={() => { setSelectedProgramId(program.id); setIsModalOpen(true); }}
              className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Modifier"
            >
              <span className="material-symbols-outlined text-[20px]">edit</span>
            </button>
          )}
        />

        <ModaleFiliere
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={loadPrograms}
          programId={selectedProgramId}
        />
      </div>
    </MiseEnPagePrincipale>
  )
}

