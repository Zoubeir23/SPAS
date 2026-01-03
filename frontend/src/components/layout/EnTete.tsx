import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useAuth } from '@/hooks/useAuth'
import { clsx } from 'clsx'
import { ROUTES } from '@/utils/constants'
import { alertService, Alert } from '@/api/services/alertService'

interface BreadcrumbItem {
  label: string
  path?: string
}

interface HeaderProps {
  breadcrumbs?: BreadcrumbItem[]
  title?: string
}

export default function EnTete({ breadcrumbs, title }: HeaderProps) {
  const { user } = useAuthStore()
  const { logout } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [unreadAlerts, setUnreadAlerts] = useState<Alert[]>([])
  const [loadingAlerts, setLoadingAlerts] = useState(false)
  const notificationsRef = useRef<HTMLDivElement>(null)

  const defaultBreadcrumbs: BreadcrumbItem[] = breadcrumbs || [
    { label: 'Accueil', path: ROUTES.DASHBOARD },
    { label: title || 'Tableau de bord' },
  ]

  // Charger les alertes non lues
  useEffect(() => {
    const loadUnreadAlerts = async () => {
      try {
        setLoadingAlerts(true)
        const alerts = await alertService.getUnread()
        setUnreadAlerts(alerts)
      } catch (error) {
        console.error('Erreur lors du chargement des alertes:', error)
      } finally {
        setLoadingAlerts(false)
      }
    }

    loadUnreadAlerts()
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(loadUnreadAlerts, 30000)
    return () => clearInterval(interval)
  }, [])

  // Fermer le dropdown si on clique en dehors
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
    }

    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showNotifications])

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await alertService.acknowledge(alertId)
      setUnreadAlerts(prev => prev.filter(alert => alert.id !== alertId))
    } catch (error) {
      console.error('Erreur lors de la reconnaissance de l\'alerte:', error)
    }
  }

  const unreadCount = unreadAlerts.length

  return (
    <header className="fixed top-0 left-0 right-0 h-[70px] bg-white dark:bg-[#1a202c] border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 z-50 shadow-sm transition-colors duration-200">
      {/* Left: Breadcrumbs */}
      <nav className="flex items-center min-w-0 mr-4">
        <ol className="flex items-center whitespace-nowrap space-x-2">
          {defaultBreadcrumbs.map((item, index) => (
            <li key={index} className="flex items-center">
              {index > 0 && (
                <span className="material-symbols-outlined text-[16px] text-gray-500 dark:text-gray-500 mx-2">
                  chevron_right
                </span>
              )}
              {item.path ? (
                <Link
                  to={item.path}
                  className="text-sm font-medium text-gray-600 hover:text-primary transition-colors dark:text-gray-400 dark:hover:text-blue-400"
                >
                  {item.label}
                </Link>
              ) : (
                <span className="text-sm font-semibold text-primary dark:text-blue-400 truncate">
                  {item.label}
                </span>
              )}
            </li>
          ))}
        </ol>
      </nav>

      {/* Center: Search Bar */}
      <div className="hidden md:flex flex-1 max-w-lg mx-4">
        <div className="relative w-full group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className="material-symbols-outlined text-gray-500 group-focus-within:text-primary transition-colors">
              search
            </span>
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher un étudiant, un cours..."
            className="block w-full pl-10 pr-20 py-2 text-sm text-gray-900 bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary placeholder-gray-400 dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500/30 transition-all"
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <span className="text-xs text-gray-400 border border-gray-200 rounded px-1.5 py-0.5 dark:border-gray-600">
              ⌘K
            </span>
          </div>
        </div>
      </div>

      {/* Right: Actions & Profile */}
      <div className="flex items-center gap-4">
        {/* Search Mobile Trigger */}
        <button className="md:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-full dark:text-gray-300 dark:hover:bg-gray-700">
          <span className="material-symbols-outlined">search</span>
        </button>

        {/* Notification Bell */}
        <div className="relative" ref={notificationsRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-gray-600 hover:text-primary hover:bg-gray-100 rounded-full transition-colors dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white relative"
          >
            <span className="material-symbols-outlined filled">notifications</span>
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500 border-2 border-white dark:border-[#1a202c]"></span>
              </span>
            )}
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white border-2 border-white dark:border-[#1a202c]">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-96 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 max-h-[500px] flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Notifications
                  {unreadCount > 0 && (
                    <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                      ({unreadCount} non lue{unreadCount > 1 ? 's' : ''})
                    </span>
                  )}
                </h3>
                <Link
                  to={ROUTES.ALERTS}
                  onClick={() => setShowNotifications(false)}
                  className="text-sm text-primary hover:text-primary-dark dark:text-blue-400 dark:hover:text-blue-300"
                >
                  Voir tout
                </Link>
              </div>

              {/* Alerts List */}
              <div className="overflow-y-auto flex-1">
                {loadingAlerts ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
                  </div>
                ) : unreadAlerts.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 px-4">
                    <span className="material-symbols-outlined text-4xl text-gray-400 mb-2">
                      notifications_off
                    </span>
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                      Aucune nouvelle notification
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200 dark:divide-gray-700">
                    {unreadAlerts.slice(0, 10).map((alert) => (
                      <div
                        key={alert.id}
                        className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                        onClick={() => {
                          handleAcknowledgeAlert(alert.id)
                          setShowNotifications(false)
                        }}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={clsx(
                              'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
                              alert.level === 'critical' || alert.level === 'high'
                                ? 'bg-red-100 dark:bg-red-900/30'
                                : alert.level === 'medium'
                                ? 'bg-yellow-100 dark:bg-yellow-900/30'
                                : 'bg-blue-100 dark:bg-blue-900/30'
                            )}
                          >
                            <span
                              className={clsx(
                                'material-symbols-outlined text-lg',
                                alert.level === 'critical' || alert.level === 'high'
                                  ? 'text-red-600 dark:text-red-400'
                                  : alert.level === 'medium'
                                  ? 'text-yellow-600 dark:text-yellow-400'
                                  : 'text-blue-600 dark:text-blue-400'
                              )}
                            >
                              {alert.type === 'attendance' ? 'event_busy' : 
                               alert.type === 'performance' ? 'trending_down' :
                               alert.type === 'risk' ? 'warning' : 'psychology'}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                              {alert.message}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {alert.studentName}
                              {alert.programName && ` • ${alert.programName}`}
                            </p>
                            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                              {alert.createdAt
                                ? new Date(alert.createdAt).toLocaleString('fr-FR', {
                                    day: 'numeric',
                                    month: 'short',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                  })
                                : 'Récemment'}
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleAcknowledgeAlert(alert.id)
                            }}
                            className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                            title="Marquer comme lu"
                          >
                            <span className="material-symbols-outlined text-lg">close</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Footer */}
              {unreadAlerts.length > 10 && (
                <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-2">
                  <Link
                    to={ROUTES.ALERTS}
                    onClick={() => setShowNotifications(false)}
                    className="text-sm text-primary hover:text-primary-dark dark:text-blue-400 dark:hover:text-blue-300 text-center block"
                  >
                    Voir {unreadAlerts.length - 10} notification{unreadAlerts.length - 10 > 1 ? 's' : ''} de plus
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Separator */}
        <div className="h-6 w-px bg-gray-200 dark:bg-gray-700"></div>

        {/* User Profile Dropdown */}
        <div className="relative group">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 p-1 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none dark:hover:bg-gray-800"
          >
            <div className="h-9 w-9 rounded-full bg-gray-200 overflow-hidden ring-2 ring-white dark:ring-gray-700 shadow-sm">
              <div className="h-full w-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-semibold">
                {user?.firstName?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
              </div>
            </div>
            <div className="hidden lg:flex flex-col items-start">
              <span className="text-sm font-semibold text-gray-900 leading-none dark:text-gray-100">
                {user?.firstName && user?.lastName
                  ? `${user.firstName} ${user.lastName}`
                  : user?.email || 'Utilisateur'}
              </span>
              <span className="text-xs text-gray-500 mt-0.5 dark:text-gray-400">
                {user?.role || 'Utilisateur'}
              </span>
            </div>
            <span
              className={clsx(
                'material-symbols-outlined text-gray-500 text-[20px] transition-transform dark:text-gray-400',
                showUserMenu && 'rotate-180'
              )}
            >
              keyboard_arrow_down
            </span>
          </button>

          {/* Dropdown Menu */}
          {showUserMenu && (
            <div className="absolute right-0 top-full mt-1 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
              {/* Header inside dropdown (Mobile name view) */}
              <div className="lg:hidden px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.firstName && user?.lastName
                    ? `${user.firstName} ${user.lastName}`
                    : user?.email || 'Utilisateur'}
                </p>
                <p className="text-xs text-gray-500 truncate dark:text-gray-400">
                  {user?.email}
                </p>
              </div>
              <div className="py-1">
                <Link
                  to={ROUTES.PROFILE}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-white group/item"
                  onClick={() => setShowUserMenu(false)}
                >
                  <span className="material-symbols-outlined text-[20px] mr-3 text-gray-500 group-hover/item:text-primary dark:text-gray-400 dark:group-hover/item:text-white">
                    person
                  </span>
                  Mon profil
                </Link>
                <Link
                  to={ROUTES.SETTINGS}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-white group/item"
                  onClick={() => setShowUserMenu(false)}
                >
                  <span className="material-symbols-outlined text-[20px] mr-3 text-gray-500 group-hover/item:text-primary dark:text-gray-400 dark:group-hover/item:text-white">
                    settings
                  </span>
                  Paramètres
                </Link>
              </div>
              <div className="border-t border-gray-100 dark:border-gray-700 my-1"></div>
              <div className="py-1">
                <button
                  onClick={() => {
                    setShowUserMenu(false)
                    logout()
                  }}
                  className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                >
                  <span className="material-symbols-outlined text-[20px] mr-3">logout</span>
                  Déconnexion
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

