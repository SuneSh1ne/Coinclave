<template>
  <div class="filter-bar">
    <div class="filter-header">
      <h3 class="filter-title">Фильтрация коллекции</h3>
      <button @click="resetFilters" class="reset-btn">Сбросить все</button>
    </div>
    
    <div class="filters-grid">
      <div class="filter-group">
        <input 
          type="text" 
          v-model="localFilters.search" 
          placeholder="Поиск по названию..."
          @input="debouncedApply"
          class="filter-input"
        >
      </div>
      
      <div class="filter-group">
        <select v-model="localFilters.country" @change="applyFilters" class="filter-select">
          <option value="">Все страны</option>
          <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <select v-model="localFilters.metal" @change="applyFilters" class="filter-select">
          <option value="">Все металлы</option>
          <option value="gold">Золото</option>
          <option value="silver">Серебро</option>
          <option value="copper">Медь</option>
          <option value="nickel">Никель</option>
          <option value="brass">Латунь</option>
          <option value="bronze">Бронза</option>
          <option value="aluminum">Алюминий</option>
          <option value="bimetallic">Биметалл</option>
        </select>
      </div>
      
      <div class="filter-group">
        <input 
          type="number" 
          v-model="localFilters.year_from" 
          placeholder="Год от"
          @input="applyFilters"
          class="filter-input"
        >
      </div>
      
      <div class="filter-group">
        <input 
          type="number" 
          v-model="localFilters.year_to" 
          placeholder="Год до"
          @input="applyFilters"
          class="filter-input"
        >
      </div>
      
      <div class="filter-group">
        <select v-model="localFilters.condition" @change="applyFilters" class="filter-select">
          <option value="">Все состояния</option>
          <option value="poor">Poor</option>
          <option value="fair">Fair</option>
          <option value="good">Good</option>
          <option value="very_good">Very Good</option>
          <option value="fine">Fine</option>
          <option value="very_fine">Very Fine</option>
          <option value="extremely_fine">Extremely Fine</option>
          <option value="uncirculated">Uncirculated</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useCoinsStore } from '../stores/coins'

const coinsStore = useCoinsStore()
const countries = coinsStore.countries

// Инициализируем с пустыми строками вместо null
const localFilters = reactive({
  country: '',
  metal: '',
  year_from: null,
  year_to: null,
  condition: '',
  search: ''
})

let debounceTimer = null
const debouncedApply = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    applyFilters()
  }, 300)
}

const applyFilters = () => {
  // Преобразуем пустые строки в null для API
  const filters = {
    country: localFilters.country || null,
    metal: localFilters.metal || null,
    year_from: localFilters.year_from,
    year_to: localFilters.year_to,
    condition: localFilters.condition || null,
    search: localFilters.search || null
  }
  coinsStore.setFilters(filters)
  coinsStore.fetchCoins()
}

const resetFilters = () => {
  localFilters.country = ''
  localFilters.metal = ''
  localFilters.year_from = null
  localFilters.year_to = null
  localFilters.condition = ''
  localFilters.search = ''
  coinsStore.resetFilters()
  coinsStore.fetchCoins()
}

onMounted(() => {
  coinsStore.fetchCountries()
})
</script>

<style scoped>
.filter-bar {
  background: white;
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 28px;
  border: 1px solid #eef2f6;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.reset-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: #f1f5f9;
  color: #3b82f6;
}

.filters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-group {
  flex: 1;
  min-width: 140px;
}

.filter-input,
.filter-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13px;
  background: white;
  transition: all 0.2s;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* Тёмная тема */
body.dark-theme .filter-bar {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .filter-title {
  color: #f1f5f9;
}

body.dark-theme .reset-btn {
  color: #94a3b8;
}

body.dark-theme .reset-btn:hover {
  background: #334155;
  color: #3b82f6;
}

body.dark-theme .filter-input,
body.dark-theme .filter-select {
  background: #0f172a;
  border-color: #334155;
  color: #f1f5f9;
}

body.dark-theme .filter-input::placeholder {
  color: #64748b;
}

body.dark-theme .filter-input:focus,
body.dark-theme .filter-select:focus {
  border-color: #3b82f6;
}
</style>