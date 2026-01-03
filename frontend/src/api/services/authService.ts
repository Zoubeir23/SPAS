import apiClient from '../axiosConfig'
import { API_ENDPOINTS } from '../endpoints'

export interface LoginCredentials {
  email: string
  password: string
  rememberMe?: boolean
}

export interface AuthResponse {
  access: string
  refresh: string
  user: {
    id: string
    email: string
    firstName?: string
    lastName?: string
    first_name?: string
    last_name?: string
    role?: string
  }
}

export interface UserProfile {
  id: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'teacher' | 'ds' | 'pedagogical'
  is_active: boolean
  avatar?: string
  avatar_url?: string
}

export interface ApiError {
  message: string
  code?: string
  detail?: string
}

/**
 * Authentication Service
 * Connects to Django REST Framework authentication endpoints
 */
export const authService = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      {
        email: credentials.email,
        password: credentials.password,
      }
    )

    // Normalize user data (handle both snake_case and camelCase)
    const user = response.data.user
    return {
      ...response.data,
      user: {
        ...user,
        firstName: user.firstName || user.first_name,
        lastName: user.lastName || user.last_name,
      },
    }
  },

  /**
   * Request password reset email
   */
  async forgotPassword(email: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, { email })
  },

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, {
      token,
      new_password: newPassword,
    })
  },

  /**
   * Change password for authenticated user
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  /**
   * Logout current session
   */
  async logout(refreshToken?: string): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
        refresh: refreshToken,
      })
    } catch {
      // Ignore logout errors - user should be logged out anyway
    }
  },

  /**
   * Logout from all devices
   */
  async logoutAll(): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT_ALL)
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await apiClient.post<{ access: string }>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh: refreshToken }
    )
    return response.data
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>(API_ENDPOINTS.AUTH.ME)
    return response.data
  },

  /**
   * Verify JWT token
   */
  async verifyToken(token: string): Promise<boolean> {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.VERIFY_TOKEN, { token })
      return true
    } catch {
      return false
    }
  },

  /**
   * Register new user (admin only)
   */
  async register(userData: {
    email: string
    password: string
    first_name: string
    last_name: string
    role: string
  }): Promise<UserProfile> {
    const response = await apiClient.post<UserProfile>(
      API_ENDPOINTS.AUTH.REGISTER,
      userData
    )
    return response.data
  },
}


