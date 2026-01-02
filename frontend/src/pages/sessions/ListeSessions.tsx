import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import Bouton from '@/components/common/Bouton'
import { sessionService, Session } from '@/api/services/sessionService'

export default function ListeSessions() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadSessions = async () => {
      setLoading(true)
      try {
        const data = await sessionService.getAll()
        setSessions(data)
      } catch (error) {
        console.error('Erreur lors du chargement des sessions:', error)
      } finally {
        setLoading(false)
      }
    }
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
          <Bouton>Nouvelle session</Bouton>
        </div>

        <TableauDonnees data={sessions} columns={columns} emptyMessage="Aucune session trouvée" />
      </div>
    </MiseEnPagePrincipale>
  )
}

