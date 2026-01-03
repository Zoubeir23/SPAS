/**
 * API Services - Central Export
 * All services are connected to Django REST Framework backend
 */

export { authService } from './authService'
export type { LoginCredentials, AuthResponse, UserProfile, ApiError } from './authService'

export { studentService } from './studentService'
export type { Student, StudentListResponse, StudentFilters } from './studentService'

export { programService, subjectService } from './programService'
export type { Program, ProgramListResponse, ProgramFilters, Subject } from './programService'

export { sessionService } from './sessionService'
export type { Session, SessionListResponse, SessionFilters } from './sessionService'

export { gradeService } from './gradeService'
export type { Grade, GradeListResponse, GradeFilters, GradeStatistics } from './gradeService'

export { attendanceService } from './attendanceService'
export type { Attendance, AttendanceListResponse, AttendanceFilters } from './attendanceService'

export { mlService } from './mlService'
export type { MLModel, MLModelListResponse, TrainingConfig, ModelPerformance } from './mlService'

export { predictionService } from './predictionService'
export type {
  Prediction,
  PredictionFactor,
  PredictionListResponse,
  PredictionFilters,
  PredictionStatistics,
  RiskDistribution,
} from './predictionService'

export { alertService } from './alertService'
export type { Alert, AlertListResponse, AlertFilters, AlertStatistics } from './alertService'

export { interventionService } from './interventionService'
export type {
  Intervention,
  InterventionListResponse,
  CreateInterventionData,
  InterventionFilters,
  InterventionStatistics,
} from './interventionService'

export { userService } from './userService'
export type { User, UserListResponse, UserFilters, CreateUserData } from './userService'

export { analyticsService } from './analyticsService'
export type {
  AnalyticsMetrics,
  DropoutEvolution,
  ProgramPerformance,
  InterventionEfficacy,
  RiskDistribution as AnalyticsRiskDistribution,
  EnrollmentEvolution,
  DashboardStats,
} from './analyticsService'

export { settingsService } from './settingsService'
export type { SystemSettings, UpdateSettingsData } from './settingsService'
