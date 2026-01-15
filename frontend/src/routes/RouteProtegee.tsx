import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { ROUTES } from '@/utils/constants'

// Types de rôles utilisateur
export type UserRole = 'admin' | 'teacher' | 'ds' | 'pedagogical'

interface ProtectedRouteProps {
  children: React.ReactNode
  /** Rôles autorisés à accéder à cette route. Si vide, tous les rôles authentifiés sont autorisés. */
  allowedRoles?: UserRole[]
  /** Rediriger vers cette route si non autorisé (défaut: dashboard) */
  redirectTo?: string
}

/**
 * Composant de protection des routes basé sur l'authentification et les rôles.
 * 
 * @example
 * // Route accessible à tous les utilisateurs authentifiés
 * <RouteProtegee><Dashboard /></RouteProtegee>
 * 
 * @example
 * // Route réservée aux admins
 * <RouteProtegee allowedRoles={['admin']}><GestionUtilisateurs /></RouteProtegee>
 * 
 * @example
 * // Route pour Data Scientists et admins
 * <RouteProtegee allowedRoles={['admin', 'ds']}><GestionModeles /></RouteProtegee>
 */
export default function RouteProtegee({ 
  children, 
  allowedRoles = [],
  redirectTo = ROUTES.DASHBOARD 
}: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore()

  // Vérifier l'authentification
  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }

  // Si des rôles sont spécifiés, vérifier que l'utilisateur a un rôle autorisé
  if (allowedRoles.length > 0 && user) {
    const userRole = user.role as UserRole
    
    if (!allowedRoles.includes(userRole)) {
      // Utilisateur authentifié mais pas le bon rôle
      console.warn(`Accès refusé: rôle "${userRole}" non autorisé pour cette route`)
      return <Navigate to={redirectTo} replace />
    }
  }

  return <>{children}</>
}

/**
 * Hook pour vérifier les permissions de l'utilisateur courant.
 */
export function usePermissions() {
  const { user } = useAuthStore()
  const role = (user?.role || 'teacher') as UserRole

  return {
    role,
    isAdmin: role === 'admin',
    isTeacher: role === 'teacher',
    isDataScientist: role === 'ds',
    isPedagogical: role === 'pedagogical',
    
    // Groupes de permissions
    canManageUsers: role === 'admin',
    canManageML: role === 'admin' || role === 'ds',
    canManageStudents: role !== 'ds',
    canViewPredictions: role !== 'teacher',
    canManageAlerts: role === 'admin' || role === 'pedagogical',
    canViewAnalytics: role !== 'teacher',
    canManageSettings: role === 'admin',
    
    // Méthode utilitaire
    hasRole: (roles: UserRole[]) => roles.includes(role),
  }
}

