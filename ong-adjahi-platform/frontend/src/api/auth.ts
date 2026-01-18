import apiClient from './client'
import type { LoginRequest, LoginResponse, User } from '../types/api'

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/login/', credentials)
    return response.data
  },

  register: async (data: any): Promise<User> => {
    const response = await apiClient.post<User>('/auth/users/register/', data)
    return response.data
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/users/me/')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.put<User>('/auth/users/update_profile/', data)
    return response.data
  },

  changePassword: async (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }): Promise<void> => {
    await apiClient.post('/auth/users/change_password/', data)
  },

  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  },
}
