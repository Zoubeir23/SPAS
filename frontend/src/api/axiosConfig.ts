import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { API_BASE_URL } from '@/utils/constants'
import { useAuthStore } from '@/store/authStore'
import { API_ENDPOINTS } from './endpoints'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Flag to prevent multiple refresh requests
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Intercepteur pour ajouter le token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les erreurs et le refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    // Si l'erreur n'est pas 401 ou si c'est une requête de refresh, rejeter
    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      originalRequest.url?.includes('refresh') ||
      originalRequest.url?.includes('login')
    ) {
      return Promise.reject(error)
    }

    // Marquer la requête comme retentée
    originalRequest._retry = true

    const refreshToken = useAuthStore.getState().refreshToken

    // Si pas de refresh token, déconnecter
    if (!refreshToken) {
      useAuthStore.getState().logout()
      window.location.href = '/auth/login'
      return Promise.reject(error)
    }

    // Si un refresh est déjà en cours, mettre en queue
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        })
        .catch((err) => Promise.reject(err))
    }

    isRefreshing = true

    try {
      // Tenter de rafraîchir le token
      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`,
        { refresh: refreshToken }
      )

      const newAccessToken = response.data.access

      // Mettre à jour le store
      useAuthStore.getState().setToken(newAccessToken)

      // Mettre à jour le header et traiter la queue
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
      processQueue(null, newAccessToken)

      return apiClient(originalRequest)
    } catch (refreshError) {
      // Si le refresh échoue, déconnecter
      processQueue(refreshError as Error, null)
      useAuthStore.getState().logout()
      window.location.href = '/auth/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default apiClient

