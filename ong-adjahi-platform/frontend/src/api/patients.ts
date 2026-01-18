import apiClient from './client'
import type { Patient } from '../types/api'

export const patientsApi = {
  getAll: async (params?: any): Promise<Patient[]> => {
    const response = await apiClient.get<Patient[]>('/patients/', { params })
    return response.data
  },

  getById: async (id: number): Promise<Patient> => {
    const response = await apiClient.get<Patient>(`/patients/${id}/`)
    return response.data
  },

  create: async (data: Partial<Patient>): Promise<Patient> => {
    const response = await apiClient.post<Patient>('/patients/', data)
    return response.data
  },

  update: async (id: number, data: Partial<Patient>): Promise<Patient> => {
    const response = await apiClient.put<Patient>(`/patients/${id}/`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/patients/${id}/`)
  },

  getStats: async (): Promise<any> => {
    const response = await apiClient.get('/patients/stats/')
    return response.data
  },
}
