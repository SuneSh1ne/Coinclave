import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    unreadCount: 0
  }),
  
  actions: {
    async register(email, password) {
      const response = await api.post('/auth/register', { email, password })
      return response.data
    },
    
    async login(email, password) {
      const response = await api.post('/auth/login', { email, password })
      this.token = response.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUserInfo()
      return response.data
    },
    
    async fetchUserInfo() {
      // Получаем статистику текущего пользователя
      try {
        const response = await api.get('/api/coins/stats/total-value')
        this.user = { total_value: response.data.total_value }
      } catch (e) {
        console.error(e)
      }
    },
    
    async fetchUnreadCount() {
      try {
        const response = await api.get('/notifications/unread-count')
        this.unreadCount = response.data.unread_count
      } catch (e) {
        console.error(e)
      }
    },
    
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})