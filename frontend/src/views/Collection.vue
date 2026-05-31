<template>
  <div class="collection-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Моя коллекция</h1>
        <p class="page-subtitle">Управление вашими нумизматическими ценностями</p>
      </div>
      <div class="header-stats">
        <div class="stat-card">
          <div class="stat-value">{{ formatPrice(totalValue) }} ₽</div>
          <div class="stat-label">Общая стоимость</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ coinsStore.total }}</div>
          <div class="stat-label">Монет в коллекции</div>
        </div>
        <button @click="exportCollection" class="btn-outline">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          Экспорт
        </button>
      </div>
    </div>

    <FilterBar />

    <div v-if="coinsStore.loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Загрузка коллекции...</p>
    </div>

    <div v-else-if="coinsStore.items.length === 0" class="empty-state">
      <h3>Коллекция пуста</h3>
      <p>Добавьте первую монету, чтобы начать систематизацию</p>
      <router-link to="/add" class="btn-add-empty">+ Добавить монету</router-link>
    </div>

    <div v-else>
      <div class="grid">
        <CoinCard
          v-for="coin in coinsStore.items"
          :key="coin.id"
          :coin="coin"
          @click="goToDetail(coin.id)"
        />
      </div>
      
      <div class="pagination" v-if="coinsStore.total > limit">
        <button 
          class="page-btn" 
          :disabled="offset === 0" 
          @click="changePage(offset - limit)"
        >
          ← Назад
        </button>
        <span class="page-info">
          {{ Math.floor(offset / limit) + 1 }} / {{ Math.ceil(coinsStore.total / limit) }}
        </span>
        <button 
          class="page-btn" 
          :disabled="offset + limit >= coinsStore.total" 
          @click="changePage(offset + limit)"
        >
          Вперёд →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCoinsStore } from '../stores/coins'
import FilterBar from '../components/FilterBar.vue'
import CoinCard from '../components/CoinCard.vue'
import api from '../api'

const router = useRouter()
const coinsStore = useCoinsStore()
const totalValue = ref(0)
const limit = ref(24)
const offset = ref(0)

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price))
}

const fetchTotalValue = async () => {
  try {
    const res = await api.get('/api/coins/stats/total-value')
    totalValue.value = res.data.total_value
  } catch (e) {
    console.error('Ошибка загрузки общей стоимости:', e)
  }
}

const goToDetail = (id) => {
  router.push(`/coin/${id}`)
}

const changePage = (newOffset) => {
  offset.value = newOffset
  coinsStore.fetchCoins(limit.value, offset.value)
}

const exportCollection = async () => {
  const format = confirm('Экспорт в Excel (CSV)? (Отмена - JSON)') ? 'csv' : 'json'
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:8000/api/coins/export/${format}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Ошибка экспорта')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `coinclave_collection.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    alert('Ошибка при экспорте коллекции')
  }
}

onMounted(() => {
  coinsStore.fetchCoins(limit.value, offset.value)
  fetchTotalValue()
})
</script>

<style scoped>
.collection-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #64748b;
  font-size: 14px;
}

.header-stats {
  display: flex;
  gap: 16px;
  align-items: center;
}

.stat-card {
  text-align: right;
  padding: 8px 16px;
  background: white;
  border-radius: 16px;
  border: 1px solid #eef2f6;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
}

.btn-outline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  color: #94a3b8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 80px 40px;
  background: white;
  border-radius: 20px;
  border: 1px solid #eef2f6;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

.empty-state p {
  color: #94a3b8;
  margin-bottom: 24px;
}

.btn-add-empty {
  display: inline-block;
  padding: 12px 28px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 30px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.btn-add-empty:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #eef2f6;
}

.page-btn {
  padding: 8px 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 30px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #64748b;
}

/* Тёмная тема */
body.dark-theme .collection-page {
  background: #0f172a;
}

body.dark-theme .page-title {
  color: #f1f5f9;
}

body.dark-theme .page-subtitle {
  color: #94a3b8;
}

body.dark-theme .stat-card {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .stat-value {
  color: #10b981;
}

body.dark-theme .stat-label {
  color: #94a3b8;
}

body.dark-theme .btn-outline {
  border-color: #475569;
  color: #94a3b8;
}

body.dark-theme .btn-outline:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #1e3a5f;
}

body.dark-theme .empty-state {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .empty-state h3 {
  color: #94a3b8;
}

body.dark-theme .empty-state p {
  color: #64748b;
}

body.dark-theme .pagination {
  border-color: #334155;
}

body.dark-theme .page-btn {
  background: #1e293b;
  border-color: #334155;
  color: #94a3b8;
}

body.dark-theme .page-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

body.dark-theme .page-info {
  color: #94a3b8;
}
</style>