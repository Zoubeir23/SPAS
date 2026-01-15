import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import Alerte from '@/components/common/Alerte'
import ModaleSession from '@/components/modals/ModaleSession'
import ModaleConfirmation from '@/components/common/ModaleConfirmation'
import { sessionService, Session } from '@/api/services/sessionService'
import { toast } from 'react-toastify'

export default function ListeSessions() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingSession, setEditingSession] = useState<Session | null>(null)
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; session: Session | null }>({
    isOpen: false,
    session: null,
  })

  const loadSessions = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await sessionService.getAll()
      setSessions(data)
    } catch (err: any) {
      console.error('Erreur lors du chargement des sessions:', err)
      setError(err.response?.data?.detail || err.message || 'Erreur lors du chargement des sessions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [])

  const columns: Column<Session>[] = [
    {
      key: 'name',
      label: 'Nom',
      sortable: true,
    },
    {
      key: 'year',
      label: 'Année',
      sortable: true,
    },
    {
      key: 'startDate',
      label: 'Date de début',
      render: (session) => new Date(session.startDate || Date.now()).toLocaleDateString('fr-FR'),
      sortable: true,
    },
    {
      key: 'endDate',
      label: 'Date de fin',
      render: (session) => new Date(session.endDate || Date.now()).toLocaleDateString('fr-FR'),
      sortable: true,
    },
    {
      key: 'status',
      label: 'Statut',
      render: (session) => {
        const variants: Record<string, 'success' | 'warning' | 'info'> = {
          active: 'success',
          inactive: 'warning',
          completed: 'info',
        }
        return <Badge variant={variants[session.status] || 'info'}>{session.status}</Badge>
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
    <MiseEnPagePrincipale title="Liste des Sessions">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Liste des Sessions
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Gérez les sessions académiques.
            </p>
          </div>
          <Bouton onClick={() => { setEditingSession(null); setIsModalOpen(true); }}>
            Nouvelle session
          </Bouton>
        </div>

        {error && (
          <Alerte type="error" onClose={() => setError(null)}>
            {error}
          </Alerte>
        )}

        <TableauDonnees
          data={sessions}
          columns={columns}
          emptyMessage="Aucune session trouvée"
          actions={(session) => (
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setEditingSession(session)
                  setIsModalOpen(true)
                }}
                className="text-gray-400 hover:text-primary p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Modifier"
              >
                <span className="material-symbols-outlined text-[20px]">edit</span>
              </button>
              <button
                onClick={() => {
                  setDeleteConfirmation({ isOpen: true, session })
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

      <ModaleSession
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingSession(null)
        }}
        sessionId={editingSession?.id}
        onSuccess={async () => {
          await loadSessions()
          setIsModalOpen(false)
          setEditingSession(null)
        }}
      />

      <ModaleConfirmation
        isOpen={deleteConfirmation.isOpen}
        onClose={() => setDeleteConfirmation({ isOpen: false, session: null })}
        onConfirm={async () => {
          if (deleteConfirmation.session) {
            try {
              await sessionService.delete(deleteConfirmation.session.id)
              await loadSessions()
              toast.success('Session supprimée avec succès')
            } catch (err) {
              console.error('Erreur lors de la suppression:', err)
              toast.error('Erreur lors de la suppression de la session')
            }
          }
        }}
        title="Supprimer la session"
        message={`Êtes-vous sûr de vouloir supprimer la session "${deleteConfirmation.session?.name}" ? Cette action est irréversible.`}
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
      />
    </MiseEnPagePrincipale>
  )
}
