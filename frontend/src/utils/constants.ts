export const APP_NAME = 'ISI Academic System'
export const APP_DESCRIPTION = "Système d'Information Académique & Analytique"

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER: 'user',
  REMEMBER_ME: 'remember_me',
} as const

export const ROUTES = {
  HOME: '/',
  LOGIN: '/auth/login',
  FORGOT_PASSWORD: '/auth/forgot-password',
  DASHBOARD: '/dashboard',
  DASHBOARD_PREDICTIVE: '/dashboard/predictive',
  STUDENTS: '/students',
  STUDENT_DETAIL: '/students/:id',
  SESSIONS: '/sessions',
  PROGRAMS: '/programs',
  ALERTS: '/alerts',
  PREDICTIONS: '/predictions',
  USERS: '/users',
  ML_MODELS: '/ml/models',
  ML_MODEL_DETAIL: '/ml/models/:id',
  ATTENDANCE: '/attendance',
  GRADES: '/grades',
  SETTINGS: '/settings',
  ANALYTICS: '/analytics',
} as const

