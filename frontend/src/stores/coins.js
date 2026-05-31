import { defineStore } from 'pinia'
import api from '../api'

export const useCoinsStore = defineStore('coins', {
  state: () => ({
    items: [],
    total: 0,
    loading: false,
    filters: {
      country: null,
      metal: null,
      year_from: null,
      year_to: null,
      condition: null,
      search: ''
    },
    countries: []
  }),
  
  actions: {
    async fetchCoins(limit = 50, offset = 0) {
      this.loading = true
      try {
        const params = {
          limit,
          offset,
          ...this.filters
        }
        // Убираем null значения
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === '') {
            delete params[key]
          }
        })
        
        const response = await api.get('/api/coins', { params })
        this.items = response.data.items
        this.total = response.data.total
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    
    async fetchCountries() {
      const response = await api.get('/api/coins/filters/countries')
      this.countries = response.data.countries
    },
    
    async deleteCoin(id) {
      await api.delete(`/api/coins/${id}`)
      await this.fetchCoins()
    },
    
    async createCoin(formData) {
      const response = await api.post('/api/coins', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    },
    
    async updateCoin(id, formData) {
      const response = await api.put(`/api/coins/${id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    },
    
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },
    
    resetFilters() {
      this.filters = {
        country: null,
        metal: null,
        year_from: null,
        year_to: null,
        condition: null,
        search: ''
      }
    },

    async fetchCoins(limit = 50, offset = 0) {
      if (this.loading) return
      this.loading = true
      try {
        const params = {
          limit,
          offset,
          ...this.filters
        }
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === '') {
            delete params[key]
          }
        })
        
        const response = await api.get('/api/coins', { params })
        this.items = response.data.items
        this.total = response.data.total
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    }
  }
})