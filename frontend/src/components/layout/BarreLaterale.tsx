import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useAuth } from '@/hooks/useAuth'
import { clsx } from 'clsx'
import Logo from '@/components/common/Logo'
import { ROUTES } from '@/utils/constants'

interface NavItem {
  label: string
  icon: string
  path: string
  children?: NavItem[]
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: 'dashboard',
    path: ROUTES.DASHBOARD,
  },
  {
    label: 'Gestion',
    icon: 'folder_managed',
    path: '#gestion',
    children: [
      { label: 'Étudiants', icon: 'school', path: '/students' },
      { label: 'Sessions', icon: 'calendar_month', path: '/sessions' },
      { label: 'Départements', icon: 'business', path: '/departments' },
      { label: 'Filières', icon: 'book_2', path: '/programs' },
      { label: 'Absences', icon: 'event_busy', path: '/attendance' },
    ],
  },
  {
    label: 'Module IA',
    icon: 'psychology',
    path: '#module-ia',
    children: [
      { label: 'Dashboard Prédictif', icon: 'dashboard', path: '/dashboard/predictive' },
      { label: 'Prédictions', icon: 'auto_awesome', path: '/predictions' },
      { label: 'Alertes', icon: 'notifications_active', path: '/alerts' },
      { label: 'Modèles ML', icon: 'model_training', path: '/ml/models' },
    ],
  },
  {
    label: 'Utilisateurs',
    icon: 'group',
    path: '/users',
  },
  {
    label: 'Analytics',
    icon: 'analytics',
    path: '/analytics',
  },
  {
    label: 'Paramètres',
    icon: 'settings',
    path: '/settings',
  },
]

interface NavItemComponentProps {
  item: NavItem
  isActive: boolean
  isExpanded: boolean
  onToggle: () => void
}

function NavItemComponent({
  item,
  isActive,
  isExpanded,
  onToggle,
}: NavItemComponentProps) {
  const hasChildren = item.children && item.children.length > 0

  if (hasChildren) {
    return (
      <div className="group/accordion">
        <button
          type="button"
          onClick={onToggle}
          className="w-full flex cursor-pointer items-center justify-between gap-3 px-3 py-3 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </div>
          <span
            className={clsx(
              'material-symbols-outlined text-slate-400 transition-transform duration-200 text-[20px]',
              isExpanded && 'rotate-180'
            )}
          >
            expand_more
          </span>
        </button>
        {isExpanded && (
          <div className="flex flex-col mt-1 space-y-1 pl-11 pr-2 pb-2">
            {(item.children ?? []).map((child, childIndex) => (
              <NavLink key={`${item.label}-${child.label}-${childIndex}`} item={child} />
            ))}
          </div>
        )}
      </div>
    )
  }

  return <NavLink item={item} isActive={isActive} />
}

function NavLink({
  item,
  isActive = false,
}: {
  item: NavItem
  isActive?: boolean
}) {
  return (
    <Link
      to={item.path}
      className={clsx(
        'flex items-center gap-3 px-3 py-3 rounded-lg transition-all border-l-[3px]',
        isActive
          ? 'bg-primary/10 text-primary border-primary'
          : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 border-transparent'
      )}
    >
      <span className="material-symbols-outlined">{item.icon}</span>
      <span className="text-sm font-medium">{item.label}</span>
    </Link>
  )
}

export default function BarreLaterale() {
  const location = useLocation()
  const { user } = useAuthStore()
  const { logout } = useAuth()
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

  // Garder le menu parent ouvert si un enfant est actif
  useEffect(() => {
    navItems.forEach((item) => {
      if (item.children) {
        const hasActiveChild = item.children.some(
          (child) => child.path === location.pathname
        )
        if (hasActiveChild) {
          setExpandedItems((prev) => {
            const next = new Set(prev)
            next.add(item.path)
            return next
          })
        }
      }
    })
  }, [location.pathname])

  const toggleExpanded = (path: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  const isItemActive = (item: NavItem): boolean => {
    if (item.path === location.pathname) return true
    if (item.children) {
      return item.children.some((child) => child.path === location.pathname)
    }
    return false
  }

  return (
    <aside className="w-[280px] h-full flex flex-col bg-white dark:bg-[#1a1f2e] border-r border-slate-200 dark:border-slate-800 shrink-0 transition-colors duration-300">
      {/* Brand Header */}
      <div className="h-20 flex items-center px-6 gap-3 shrink-0 border-b border-slate-200 dark:border-slate-800">
        <Logo size="sm" variant="compact" showText={true} />
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
        {navItems.map((item, index) => (
          <NavItemComponent
            key={`${item.label}-${index}`}
            item={item}
            isActive={isItemActive(item)}
            isExpanded={expandedItems.has(item.path)}
            onToggle={() => toggleExpanded(item.path)}
          />
        ))}
      </nav>

      {/* Footer User Profile */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 shrink-0">
        <div className="flex items-center justify-between gap-3 p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="bg-center bg-no-repeat bg-cover rounded-full h-10 w-10 shrink-0 border border-slate-200 dark:border-slate-700 shadow-sm bg-gray-200 dark:bg-gray-700"></div>
            <div className="flex flex-col min-w-0">
              <p className="text-slate-900 dark:text-white text-sm font-semibold truncate">
                {user?.firstName && user?.lastName
                  ? `${user.firstName} ${user.lastName}`
                  : user?.email || 'Utilisateur'}
              </p>
              <p className="text-slate-500 dark:text-slate-400 text-xs truncate">
                {user?.role || 'Utilisateur'}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="text-slate-400 hover:text-red-500 transition-colors shrink-0"
            title="Déconnexion"
          >
            <span className="material-symbols-outlined text-[20px]">logout</span>
          </button>
        </div>
      </div>
    </aside>
  )
}

