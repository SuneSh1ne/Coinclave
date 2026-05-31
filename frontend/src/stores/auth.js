import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token')
  }),
  
  actions: {
    async register(email, username, password) {
      const response = await api.post('/auth/register', { email, username, password })
      return response.data
    },
    
    async login(email, password) {
      const response = await api.post('/auth/login', { email, password })
      this.token = response.data.access_token
      this.isAuthenticated = true
      localStorage.setItem('token', this.token)
      await this.fetchUserInfo()
      return response.data
    },
    
    async fetchUserInfo() {
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
        localStorage.setItem('username', this.user.username || '')
        localStorage.setItem('userEmail', this.user.email)
      } catch (e) {
        console.error(e)
      }
    },
    
    async fetchUnreadCount() {
      try {
        const response = await api.get('/notifications/unread-count')
        this.unreadCount = response.data.unread_count
      } catch (e) {}
    },
    
    logout() {
      this.token = null
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userEmail')
    }
  }
})