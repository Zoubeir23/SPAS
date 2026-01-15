import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import BarreRecherche from '@/components/common/BarreRecherche'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import Alerte from '@/components/common/Alerte'
import ModaleAbsence from '@/components/modals/ModaleAbsence'
import ModaleConfirmation from '@/components/common/ModaleConfirmation'
import { attendanceService, Attendance } from '@/api/services/attendanceService'
import { toast } from 'react-toastify'

export default function GestionAbsences() {
  const [attendances, setAttendances] = useState<Attendance[]>([])
  const [filteredAttendances, setFilteredAttendances] = useState<Attendance[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingAttendance, setEditingAttendance] = useState<Attendance | null>(null)
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; attendance: Attendance | null }>({
    isOpen: false,
    attendance: null,
  })

  const loadAttendances = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await attendanceService.getAll()
      setAttendances(data)
      setFilteredAttendances(data)
    } catch (err: any) {
      console.error('Erreur lors du chargement des absences:', err)
      setError(err.response?.data?.detail || err.message || 'Erreur lors du chargement des absences')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
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
          <Bouton onClick={() => { setEditingAttendance(null); setIsModalOpen(true); }}>
            <span className="material-symbols-outlined text-[20px]">add</span>
            Saisir une absence
          </Bouton>
        </div>

        {error && (
          <Alerte type="error" onClose={() => setError(null)}>
            {error}
          </Alerte>
        )}

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
          actions={(attendance) => (
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setEditingAttendance(attendance)
                  setIsModalOpen(true)
                }}
                className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Modifier"
              >
                <span className="material-symbols-outlined text-[20px]">edit</span>
              </button>
              <button
                onClick={() => {
                  setDeleteConfirmation({ isOpen: true, attendance })
                }}
                className="text-gray-400 hover:text-red-500 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Supprimer"
              >
                <span className="material-symbols-outlined text-[20px]">delete</span>
              </button>
            </div>
          )}
        />
      </div>

      <ModaleAbsence
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingAttendance(null)
        }}
        attendanceId={editingAttendance?.id}
        onSuccess={async () => {
          await loadAttendances()
          setIsModalOpen(false)
          setEditingAttendance(null)
        }}
      />

      <ModaleConfirmation
        isOpen={deleteConfirmation.isOpen}
        onClose={() => setDeleteConfirmation({ isOpen: false, attendance: null })}
        onConfirm={async () => {
          if (deleteConfirmation.attendance) {
            try {
              await attendanceService.delete(deleteConfirmation.attendance.id)
              await loadAttendances()
              toast.success('Absence supprimée avec succès')
            } catch (err) {
              console.error('Erreur lors de la suppression:', err)
              toast.error('Erreur lors de la suppression de l\'absence')
            }
          }
        }}
        title="Supprimer l'absence"
        message="Êtes-vous sûr de vouloir supprimer cette absence ? Cette action est irréversible."
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
      />
    </MiseEnPagePrincipale>
  )
}
