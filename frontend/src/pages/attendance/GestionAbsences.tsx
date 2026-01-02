import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import BarreRecherche from '@/components/common/BarreRecherche'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import { attendanceService, Attendance } from '@/api/services/attendanceService'

export default function GestionAbsences() {
  const [attendances, setAttendances] = useState<Attendance[]>([])
  const [filteredAttendances, setFilteredAttendances] = useState<Attendance[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const loadAttendances = async () => {
      setLoading(true)
      try {
        const data = await attendanceService.getAll()
        setAttendances(data)
        setFilteredAttendances(data)
      } catch (error) {
        console.error('Erreur lors du chargement des absences:', error)
      } finally {
        setLoading(false)
      }
    }
    loadAttendances()
  }, [])

  useEffect(() => {
    let filtered = attendances

    if (searchQuery) {
      filtered = filtered.filter(
        (a) =>
          (a.studentName ?? '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (a.subjectName && a.subjectName.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }

    setFilteredAttendances(filtered)
  }, [searchQuery, attendances])

  const columns: Column<Attendance>[] = [
    {
      key: 'studentName',
      label: 'Étudiant',
      sortable: true,
    },
    {
      key: 'date',
      label: 'Date',
      render: (attendance) => new Date(attendance.date).toLocaleDateString('fr-FR'),
      sortable: true,
    },
    {
      key: 'subjectName',
      label: 'Matière',
      render: (attendance) => attendance.subjectName || '-',
    },
    {
      key: 'status',
      label: 'Statut',
      render: (attendance) => {
        const variants: Record<string, 'danger' | 'warning' | 'info' | 'success'> = {
          absent: 'danger',
          late: 'warning',
          excused: 'info',
          present: 'success',
        }
        const labels: Record<string, string> = {
          absent: 'Absent',
          late: 'En retard',
          excused: 'Justifié',
          present: 'Présent',
        }
        return (
          <Badge variant={variants[attendance.status] || 'info'}>
            {labels[attendance.status] || attendance.status}
          </Badge>
        )
      },
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
    <MiseEnPagePrincipale title="Gestion des Absences">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Gestion des Absences
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Gérez les absences et la présence des étudiants.
            </p>
          </div>
          <Bouton>
            <span className="material-symbols-outlined text-[20px]">add</span>
            Saisir une absence
          </Bouton>
        </div>

        <div className="bg-white dark:bg-surface-dark rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 min-w-[240px]">
              <BarreRecherche
                placeholder="Rechercher par étudiant ou matière..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
          </div>
        </div>

        <TableauDonnees
          data={filteredAttendances}
          columns={columns}
          emptyMessage="Aucune absence enregistrée"
        />
      </div>
    </MiseEnPagePrincipale>
  )
}
