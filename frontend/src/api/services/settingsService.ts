import apiClient from '../axiosConfig'

export interface SystemSettings {
  // ML Settings
  ml_auto_training: boolean
  ml_training_frequency: 'daily' | 'weekly' | 'monthly'
  ml_risk_threshold_low: number
  ml_risk_threshold_medium: number
  ml_risk_threshold_high: number
  
  // Alert Settings
  alert_auto_create: boolean
  alert_email_notifications: boolean
  alert_sms_notifications: boolean
  
  // Notification Settings
  notification_email_enabled: boolean
  notification_sms_enabled: boolean
  notification_push_enabled: boolean
  
  // Academic Settings
  academic_year_start_month: number
  academic_passing_grade: number
  academic_attendance_threshold: number
  
  // System Settings
  system_language: 'fr' | 'en'
  system_timezone: string
  system_date_format: string
  system_maintenance_mode: boolean
  
  // Data Retention
  data_retention_years: number
  
  // Metadata
  created_at?: string
  updated_at?: string
  updated_by_name?: string
}

export type UpdateSettingsData = Partial<SystemSettings>

export const settingsService = {
  /**
   * Récupère les paramètres système actuels
   */
  async getSettings(): Promise<SystemSettings> {
    const response = await apiClient.get<SystemSettings>('/core/settings/')
    return response.data
  },

  /**
   * Met à jour les paramètres système (admin uniquement)
   */
  async updateSettings(data: UpdateSettingsData): Promise<SystemSettings> {
    const response = await apiClient.patch<SystemSettings>('/core/settings/', data)
    return response.data
  },

  /**
   * Réinitialise les paramètres aux valeurs par défaut (admin uniquement)
   */
  async resetSettings(): Promise<{ message: string; data: SystemSettings }> {
    const response = await apiClient.post<{ message: string; data: SystemSettings }>('/core/settings/reset/')
    return response.data
  }
}

export default settingsService
