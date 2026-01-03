import { ReactNode, useState } from 'react'
import BarreLaterale from './BarreLaterale'
import EnTete from './EnTete'
import { useLocation } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'

interface MainLayoutProps {
  children: ReactNode
  title?: string
  breadcrumbs?: Array<{ label: string; path?: string }>
}

export default function MiseEnPagePrincipale({
  children,
  title,
  breadcrumbs,
}: MainLayoutProps) {
  const location = useLocation()
  const [_sidebarOpen, _setSidebarOpen] = useState(true)

  // Générer les breadcrumbs automatiquement si non fournis
  const getBreadcrumbs = () => {
    if (breadcrumbs) return breadcrumbs

    const pathMap: Record<string, string> = {
      [ROUTES.DASHBOARD]: 'Dashboard Général',
      [ROUTES.DASHBOARD_PREDICTIVE]: 'Dashboard Prédictif',
      [ROUTES.STUDENTS]: 'Étudiants',
      [ROUTES.SESSIONS]: 'Sessions',
      [ROUTES.PROGRAMS]: 'Filières',
      [ROUTES.ALERTS]: 'Alertes',
      [ROUTES.USERS]: 'Utilisateurs',
      [ROUTES.ML_MODELS]: 'Modèles ML',
      [ROUTES.ATTENDANCE]: 'Absences',
      [ROUTES.GRADES]: 'Notes',
      [ROUTES.SETTINGS]: 'Paramètres',
      [ROUTES.PROFILE]: 'Mon Profil',
      [ROUTES.ANALYTICS]: 'Analytics',
    }

    const currentPath = location.pathname
    const currentLabel = pathMap[currentPath] || title || 'Page'

    return [
      { label: 'Accueil', path: ROUTES.DASHBOARD },
      { label: currentLabel },
    ]
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background-light dark:bg-background-dark">
      {/* Sidebar */}
      <BarreLaterale />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Header */}
        <EnTete breadcrumbs={getBreadcrumbs()} title={title} />

        {/* Content */}
        <main className="flex-1 overflow-y-auto pt-[70px] bg-background-light dark:bg-background-dark">
          <div className="p-4 md:p-8">{children}</div>
        </main>
      </div>
    </div>
  )
}

