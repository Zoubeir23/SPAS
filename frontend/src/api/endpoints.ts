/**
 * API Endpoints Configuration
 * Maps to Django REST Framework backend endpoints
 */
export const API_ENDPOINTS = {
  // Authentication endpoints (apps/authentication)
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    LOGOUT_ALL: '/auth/logout-all/',
    REGISTER: '/auth/register/',
    VERIFY_EMAIL: '/auth/verify-email/',
    RESEND_VERIFICATION: '/auth/resend-verification/',
    REFRESH: '/auth/token/refresh/',
    VERIFY_TOKEN: '/auth/token/verify/',
    FORGOT_PASSWORD: '/auth/password/forgot/',
    RESET_PASSWORD: '/auth/password/reset/',
    CHANGE_PASSWORD: '/auth/password/change/',
    CHECK_PASSWORD_STRENGTH: '/auth/password/check-strength/',
    ME: '/auth/me/',
    ACTIVITY: '/auth/activity/',
  },

  // Users endpoints (apps/users)
  USERS: {
    LIST: '/users/',
    BASE: '/users/',
    BY_ID: (id: string) => `/users/${id}/`,
    CHANGE_PASSWORD: (id: string) => `/users/${id}/change-password/`,
    ME: '/users/me/',
    ACTIVATE: (id: string) => `/users/${id}/activate/`,
    DEACTIVATE: (id: string) => `/users/${id}/deactivate/`,
  },

  // Students endpoints (apps/students)
  STUDENTS: {
    BASE: '/students/',
    BY_ID: (id: string) => `/students/${id}/`,
    GRADES: (id: string) => `/students/${id}/grades/`,
    ATTENDANCE: (id: string) => `/students/${id}/attendance/`,
    PREDICTIONS: (id: string) => `/students/${id}/predictions/`,
    AT_RISK: '/students/at_risk/',
    EXPORT_CSV: '/students/export_csv/',
    IMPORT_CSV: '/students/import_csv/',
  },

  // Departments endpoints (apps/programs)
  DEPARTMENTS: {
    BASE: '/programs/departments/',
    BY_ID: (id: string) => `/programs/departments/${id}/`,
    PROGRAMS: (id: string) => `/programs/departments/${id}/programs/`,
  },

  // Programs endpoints (apps/programs)
  PROGRAMS: {
    BASE: '/programs/programs/',
    BY_ID: (id: string) => `/programs/programs/${id}/`,
    STUDENTS: (id: string) => `/programs/programs/${id}/students/`,
  },

  // Subjects endpoints (apps/programs)
  SUBJECTS: {
    BASE: '/programs/subjects/',
    BY_ID: (id: string) => `/programs/subjects/${id}/`,
  },

  // Sessions endpoints (apps/sessions)
  SESSIONS: {
    BASE: '/sessions/sessions/',
    BY_ID: (id: string) => `/sessions/sessions/${id}/`,
    STUDENTS: (id: string) => `/sessions/sessions/${id}/students/`,
  },

  // Grades endpoints (apps/grades)
  GRADES: {
    BASE: '/grades/grades/',
    BY_ID: (id: string) => `/grades/grades/${id}/`,
    BY_STUDENT: (studentId: string) => `/grades/grades/student/${studentId}/`,
    BULK_CREATE: '/grades/grades/bulk-create/',
    STATISTICS: '/grades/grades/statistics/',
    EXPORT_CSV: '/grades/grades/export_csv/',
    IMPORT_CSV: '/grades/grades/import_csv/',
  },

  // Attendance endpoints (apps/attendance)
  ATTENDANCE: {
    BASE: '/attendance/attendance/',
    BY_ID: (id: string) => `/attendance/attendance/${id}/`,
    BY_STUDENT: (studentId: string) => `/attendance/attendance/student/${studentId}/`,
  },

  // ML Models endpoints (apps/ml)
  ML: {
    MODELS: '/ml/models/',
    MODEL_BY_ID: (id: string) => `/ml/models/${id}/`,
    TRAIN: (id: string) => `/ml/models/${id}/train/`,
    ACTIVE: '/ml/models/active/',
    PERFORMANCE: '/ml/models/performance/',
    TRAINING_JOBS: '/ml/training-jobs/',
  },

  // Predictions endpoints (apps/predictions)
  PREDICTIONS: {
    BASE: '/predictions/predictions/',
    BY_ID: (id: string) => `/predictions/predictions/${id}/`,
    BY_STUDENT: (studentId: string) => `/predictions/predictions/student/${studentId}/`,
    HIGH_RISK: '/predictions/predictions/high_risk/',
    STATISTICS: '/predictions/predictions/statistics/',
    DISTRIBUTION: '/predictions/predictions/distribution/',
    GENERATE: '/predictions/predictions/generate/',
  },

  // Alerts endpoints (apps/alerts)
  ALERTS: {
    BASE: '/alerts/alerts/',
    BY_ID: (id: string) => `/alerts/alerts/${id}/`,
    ACKNOWLEDGE: (id: string) => `/alerts/alerts/${id}/acknowledge/`,
    RESOLVE: (id: string) => `/alerts/alerts/${id}/resolve/`,
    UNREAD: '/alerts/alerts/unread/',
    STATISTICS: '/alerts/alerts/statistics/',
    BY_TYPE: '/alerts/alerts/by_type/',
    BY_STUDENT: (studentId: string) => `/alerts/alerts/student/${studentId}/`,
  },

  // Interventions endpoints (apps/alerts)
  INTERVENTIONS: {
    BASE: '/alerts/interventions/',
    BY_ID: (id: string) => `/alerts/interventions/${id}/`,
    COMPLETE: (id: string) => `/alerts/interventions/${id}/complete/`,
    CANCEL: (id: string) => `/alerts/interventions/${id}/cancel/`,
    BY_STUDENT: (studentId: string) => `/alerts/interventions/student/${studentId}/`,
    PENDING: '/alerts/interventions/pending/',
    STATISTICS: '/alerts/interventions/statistics/',
  },

  // Analytics endpoints (apps/analytics)
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard/',
    METRICS: '/analytics/metrics/',
    RISK_DISTRIBUTION: '/analytics/risk-distribution/',
    DROPOUT_EVOLUTION: '/analytics/dropout-evolution/',
    PROGRAM_PERFORMANCE: '/analytics/program-performance/',
    INTERVENTION_EFFICACY: '/analytics/intervention-efficacy/',
    MODEL_PERFORMANCE: '/analytics/model-performance/',
    PREDICTION_FACTORS: (studentId: string) => `/analytics/prediction-factors/${studentId}/`,
    RISK_EVOLUTION: (studentId: string) => `/analytics/risk-evolution/${studentId}/`,
  },
} as const

// Type helper for dynamic endpoints
export type EndpointFunction = (id: string) => string

