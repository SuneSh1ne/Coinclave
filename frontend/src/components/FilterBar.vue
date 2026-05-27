<template>
  <div class="filter-bar card">
    <h3>Фильтры</h3>
    <div class="filters-grid">
      <div class="filter-group">
        <label>Поиск по названию</label>
        <input type="text" v-model="localFilters.search" placeholder="Название монеты..." @input="applyFilters">
      </div>
      
      <div class="filter-group">
        <label>Страна</label>
        <select v-model="localFilters.country" @change="applyFilters">
          <option value="">Все страны</option>
          <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Металл</label>
        <select v-model="localFilters.metal" @change="applyFilters">
          <option value="">Все</option>
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
        <label>Год от</label>
        <input type="number" v-model="localFilters.year_from" @input="applyFilters">
      </div>
      
      <div class="filter-group">
        <label>Год до</label>
        <input type="number" v-model="localFilters.year_to" @input="applyFilters">
      </div>
      
      <div class="filter-group">
        <label>Состояние</label>
        <select v-model="localFilters.condition" @change="applyFilters">
          <option value="">Все</option>
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
      
      <div class="filter-group">
        <button @click="resetFilters" class="btn-secondary">Сбросить</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { useCoinsStore } from '../stores/coins'

const coinsStore = useCoinsStore()
const countries = coinsStore.countries

const localFilters = reactive({
  country: null,
  metal: null,
  year_from: null,
  year_to: null,
  condition: null,
  search: ''
})

const applyFilters = () => {
  coinsStore.setFilters(localFilters)
  coinsStore.fetchCoins()
}

const resetFilters = () => {
  localFilters.country = null
  localFilters.metal = null
  localFilters.year_from = null
  localFilters.year_to = null
  localFilters.condition = null
  localFilters.search = ''
  coinsStore.resetFilters()
  coinsStore.fetchCoins()
}

// Загружаем страны при монтировании
import { onMounted } from 'vue'
onMounted(() => {
  coinsStore.fetchCountries()
})
</script>

<style scoped>
.filter-bar {
  margin-bottom: 20px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 13px;
  color: #666;
}

.filter-group input,
.filter-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 5px;
}
</style>