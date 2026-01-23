import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import BarreRecherche from '@/components/common/BarreRecherche'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import ModaleEtudiant from '@/components/modals/ModaleEtudiant'
import { studentService, Student } from '@/api/services/studentService'
import { ROUTES } from '@/utils/constants'

export default function ListeEtudiants() {
  const navigate = useNavigate()
  const [students, setStudents] = useState<Student[]>([])
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedProgram, setSelectedProgram] = useState<string>('all')
  const [isStudentModalOpen, setIsStudentModalOpen] = useState(false)

  useEffect(() => {
    const loadStudents = async () => {
      setLoading(true)
      try {
        const data = await studentService.getAll()
        setStudents(data)
        setFilteredStudents(data)
      } catch (error) {
        console.error('Erreur lors du chargement des étudiants:', error)
      } finally {
        setLoading(false)
      }
    }
    loadStudents()
  }, [])

  useEffect(() => {
    let filtered = students

    if (searchQuery) {
      filtered = filtered.filter(
        (s) =>
          (s.firstName ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (s.lastName ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          s.matricule.includes(searchQuery) ||
          s.email.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (selectedProgram !== 'all') {
      filtered = filtered.filter((s) => s.programId === selectedProgram)
    }

    setFilteredStudents(filtered)
  }, [searchQuery, selectedProgram, students])

  const getRiskBadge = (student: Student) => {
    if (!student.riskLevel) {
      return <Badge variant="success">Normal</Badge>
    }

    switch (student.riskLevel) {
      case 'critical':
        return (
          <Badge variant="danger" className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-600 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-600"></span>
            </span>
            Critique
          </Badge>
        )
      case 'high':
        return (
          <Badge variant="danger" className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            Risque Élevé
          </Badge>
        )
      case 'medium':
        return <Badge variant="warning">Risque Moyen</Badge>
      case 'low':
        return <Badge variant="success">Faible Risque</Badge>
      default:
        return <Badge variant="success">Normal</Badge>
    }
  }

  const columns: Column<Student>[] = [
    {
      key: 'matricule',
      label: 'Matricule',
      render: (student) => (
        <span className="text-sm font-medium text-gray-500 font-mono">
          {student.matricule}
        </span>
      ),
      sortable: true,
    },
    {
      key: 'name',
      label: 'Étudiant',
      render: (student) => (
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
            {(student.firstName ?? 'X')[0]}
            {(student.lastName ?? 'X')[0]}
          </div>
          <div>
            <div className="text-sm font-semibold text-gray-900 dark:text-white">
              {student.firstName} {student.lastName}
            </div>
            <div className="text-xs text-gray-500">{student.email}</div>
          </div>
        </div>
      ),
      sortable: true,
    },
    {
      key: 'programName',
      label: 'Filière',
      render: (student) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {student.programName}
        </span>
      ),
      sortable: true,
    },
    {
      key: 'status',
      label: 'Statut / Risque',
      render: (student) => getRiskBadge(student),
    },
  ]

  const handleRowClick = (student: Student) => {
    navigate(`${ROUTES.STUDENTS}/${student.id}`)
  }

  const handleStudentCreated = async () => {
    // Recharger la liste des étudiants
    setLoading(true)
    try {
      const data = await studentService.getAll()
      setStudents(data)
      setFilteredStudents(data)
    } catch (error) {
      console.error('Erreur lors du rechargement des étudiants:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleActions = (student: Student) => (
    <div className="flex items-center gap-2">
      <button
        onClick={(e) => {
          e.stopPropagation()
          navigate(`${ROUTES.STUDENTS}/${student.id}`)
        }}
        className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="Voir détails"
      >
        <span className="material-symbols-outlined text-[20px]">visibility</span>
      </button>
      <button
        onClick={(e) => {
          e.stopPropagation()
          // TODO: Ouvrir modale d'édition
        }}
        className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="Modifier"
      >
        <span className="material-symbols-outlined text-[20px]">edit</span>
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
    <MiseEnPagePrincipale title="Liste des Étudiants">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        {/* Page Heading & Actions */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Liste des Étudiants
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Gérez les inscriptions, les filières et suivez les risques.
            </p>
          </div>
              <Bouton
            onClick={() => setIsStudentModalOpen(true)}
            className="w-full md:w-auto"
          >
            <span className="material-symbols-outlined text-[20px]">add</span>
            Nouvel étudiant
              </Bouton>
        </div>

        {/* Filters & Toolbar */}
        <div className="bg-white dark:bg-surface-dark rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div className="flex flex-col lg:flex-row gap-4 justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-lg">
              <BarreRecherche
                placeholder="Rechercher par nom, matricule..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>

            {/* Filter Chips */}
            <div className="flex flex-wrap items-center gap-3">
              <select
                value={selectedProgram}
                onChange={(e) => setSelectedProgram(e.target.value)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750 text-sm font-medium text-gray-700 dark:text-gray-200 transition-colors"
              >
                <option value="all">Filière: Toutes</option>
                <option value="1">Informatique</option>
                <option value="2">Génie Logiciel</option>
              </select>
            </div>
          </div>
        </div>

        {/* Data Table */}
          <TableauDonnees
          data={filteredStudents}
          columns={columns}
          onRowClick={handleRowClick}
          actions={handleActions}
          emptyMessage="Aucun étudiant trouvé"
        />

        {/* Student Modal */}
        <ModaleEtudiant
          isOpen={isStudentModalOpen}
          onClose={() => setIsStudentModalOpen(false)}
          onSuccess={handleStudentCreated}
        />
      </div>
    </MiseEnPagePrincipale>
  )
}

