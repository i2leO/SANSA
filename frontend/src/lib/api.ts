import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const clearStoredAuth = () => {
  useAuthStore.getState().logout()
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('auth-storage')
}

let refreshRequest: Promise<string> | null = null
class SessionChangedError extends Error {}

const refreshAccessToken = () => {
  if (!refreshRequest) {
    refreshRequest = (async () => {
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) throw new Error('Missing refresh token')
      const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
      if (localStorage.getItem('refreshToken') !== refreshToken) throw new SessionChangedError('Session changed during refresh')
      const user = useAuthStore.getState().user
      if (!user || !data.access_token || !data.refresh_token) throw new Error('Invalid session')
      useAuthStore.getState().login(user, data.access_token, data.refresh_token)
      return data.access_token as string
    })().finally(() => { refreshRequest = null })
  }
  return refreshRequest
}

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    const participantToken = sessionStorage.getItem('participantToken')
    if (participantToken) config.headers['X-Respondent-Token'] = participantToken
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (!originalRequest || error.response?.status !== 401 || originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/participant-auth/login')) {
      return Promise.reject(error)
    }
    if (error.response?.status === 401 && sessionStorage.getItem('participantToken') && !localStorage.getItem('accessToken') && !originalRequest?.url?.includes('/participant-auth/login')) {
      sessionStorage.removeItem('participantToken')
      localStorage.removeItem('auth-storage')
      window.location.href = '/start'
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Another request may already have refreshed while this response was in flight.
        const currentToken = localStorage.getItem('accessToken')
        if (currentToken && originalRequest.headers.Authorization !== `Bearer ${currentToken}`) {
          originalRequest.headers.Authorization = `Bearer ${currentToken}`
          return apiClient(originalRequest)
        }
        const accessToken = await refreshAccessToken()
        originalRequest.headers.Authorization = `Bearer ${accessToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        if (refreshError instanceof SessionChangedError) return Promise.reject(refreshError)
        clearStoredAuth()
        window.location.href = '/admin/login'
        return Promise.reject(refreshError)
      }
    }

    if (error.response?.status === 401) {
      clearStoredAuth()
      window.location.href = '/admin/login'
    }

    return Promise.reject(error)
  }
)

export default apiClient
