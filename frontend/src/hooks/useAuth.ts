import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authService, type LoginCredentials } from '@/api/services/authService'
import { ROUTES } from '@/utils/constants'

/**
 * Détermine la route de redirection selon le rôle de l'utilisateur
 */
function getDashboardByRole(role?: string): string {
  switch (role) {
    case 'ds':
      // Data Scientist → Dashboard Prédictif
      return ROUTES.DASHBOARD_PREDICTIVE
    case 'admin':
    case 'teacher':
    case 'pedagogical':
    default:
      // Admin, Enseignant, Direction Pédagogique → Dashboard Général
      return ROUTES.DASHBOARD
  }
}

export function useAuth() {
  const navigate = useNavigate()
  const { login: setAuth, logout: clearAuth, isLoading, setLoading } = useAuthStore()

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setLoading(true)
        const response = await authService.login(credentials)
        setAuth(
          response.access,
          response.refresh,
          response.user
        )
        // Redirection selon le rôle de l'utilisateur
        const redirectRoute = getDashboardByRole(response.user.role)
        navigate(redirectRoute)
        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Une erreur est survenue',
        }
      } finally {
        setLoading(false)
      }
    },
    [navigate, setAuth, setLoading]
  )

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    } finally {
      clearAuth()
      navigate(ROUTES.LOGIN)
    }
  }, [clearAuth, navigate])

  const checkAuth = useCallback(() => {
    const { token, user } = useAuthStore.getState()
    return !!(token && user)
  }, [])

  return {
    login,
    logout,
    checkAuth,
    isLoading,
  }
}

