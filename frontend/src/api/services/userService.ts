import apiClient from '../axiosConfig';
import { API_ENDPOINTS } from '../endpoints';

export interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  first_name?: string;
  last_name?: string;
  role: 'admin' | 'teacher' | 'ds' | 'pedagogical';
  is_active?: boolean;
  isActive?: boolean;
  created_at?: string;
  updated_at?: string;
  last_login?: string;
}

export interface UserListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: User[];
}

export interface UserFilters {
  search?: string;
  role?: string;
  is_active?: boolean;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface CreateUserData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: string;
}

function normalizeUser(user: User): User {
  return {
    ...user,
    firstName: user.firstName || user.first_name,
    lastName: user.lastName || user.last_name,
    isActive: user.isActive ?? user.is_active ?? true,
  };
}

export const userService = {
  async getAll(filters?: UserFilters): Promise<UserListResponse> {
    const response = await apiClient.get<UserListResponse>(API_ENDPOINTS.USERS.LIST, { params: filters });
    return {
      ...response.data,
      results: response.data.results.map(normalizeUser),
    };
  },

  async getById(id: string): Promise<User> {
    const response = await apiClient.get<User>(API_ENDPOINTS.USERS.BY_ID(id));
    return normalizeUser(response.data);
  },

  async create(data: CreateUserData): Promise<User> {
    const response = await apiClient.post<User>(API_ENDPOINTS.USERS.LIST, data);
    return normalizeUser(response.data);
  },

  async update(id: string, data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>(API_ENDPOINTS.USERS.BY_ID(id), data);
    return normalizeUser(response.data);
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.USERS.BY_ID(id));
  },

  async changePassword(id: string, oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.USERS.CHANGE_PASSWORD(id), {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>(API_ENDPOINTS.USERS.ME);
    return normalizeUser(response.data);
  },

  async activate(id: string): Promise<User> {
    const response = await apiClient.post<User>(API_ENDPOINTS.USERS.ACTIVATE(id));
    return normalizeUser(response.data);
  },

  async deactivate(id: string): Promise<User> {
    const response = await apiClient.post<User>(API_ENDPOINTS.USERS.DEACTIVATE(id));
    return normalizeUser(response.data);
  },
};

export default userService;
