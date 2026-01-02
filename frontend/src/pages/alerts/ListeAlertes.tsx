import { useState, useEffect } from 'react'
import MiseEnPagePrincipale from '@/components/layout/MiseEnPagePrincipale'
import TableauDonnees, { Column } from '@/components/common/TableauDonnees'
import Badge from '@/components/common/Badge'
import { alertService, Alert } from '@/api/services/alertService'

export default function ListeAlertes() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadAlerts = async () => {
      setLoading(true)
      try {
        const data = await alertService.getAll()
        setAlerts(data)
      } catch (error) {
        console.error('Erreur lors du chargement des alertes:', error)
      } finally {
        setLoading(false)
      }
    }
    loadAlerts()
  }, [])

  const columns: Column<Alert>[] = [
    {
      key: 'studentName',
      label: 'Étudiant',
      sortable: true,
    },
    {
      key: 'type',
      label: 'Type',
      render: (alert) => (
        <Badge variant="info">{alert.type}</Badge>
      ),
    },
    {
      key: 'level',
      label: 'Niveau',
      render: (alert) => {
        const variants: Record<string, 'danger' | 'warning' | 'info'> = {
          critical: 'danger',
          high: 'danger',
          medium: 'warning',
          low: 'info',
        }
        return <Badge variant={variants[alert.level] || 'info'}>{alert.level}</Badge>
      },
    },
    {
      key: 'message',
      label: 'Message',
    },
    {
      key: 'status',
      label: 'Statut',
      render: (alert) => (
        <Badge variant={alert.status === 'resolved' ? 'success' : 'warning'}>
          {alert.status}
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
    <MiseEnPagePrincipale title="Liste des Alertes">
      <div className="mx-auto max-w-7xl flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white tracking-tight">
              Liste des Alertes
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Gérez les alertes prédictives et les notifications.
            </p>
          </div>
        </div>

        <TableauDonnees data={alerts} columns={columns} emptyMessage="Aucune alerte trouvée" />
      </div>
    </MiseEnPagePrincipale>
  )
}

