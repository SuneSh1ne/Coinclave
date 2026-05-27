<template>
  <div class="collection-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Коллекция</h1>
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
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
      </div>
      <h3>Коллекция пуста</h3>
      <p>Добавьте первую монету, чтобы начать систематизацию</p>
      <router-link to="/add" class="btn-primary">Добавить монету</router-link>
    </div>

    <div v-else>
      <div class="grid">
        <CoinCard
          v-for="coin in coinsStore.items"
          :key="coin.id"
          :coin="coin"
          @click="goToDetail(coin.id)"
          @delete="deleteCoin(coin.id)"
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
import { ref, onMounted, computed } from 'vue'
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
  } catch (e) {}
}

const goToDetail = (id) => {
  router.push(`/coin/${id}`)
}

const deleteCoin = async (id) => {
  if (confirm('Удалить монету из коллекции?')) {
    await coinsStore.deleteCoin(id)
    await fetchTotalValue()
    await coinsStore.fetchCoins(limit.value, offset.value)
  }
}

const changePage = (newOffset) => {
  offset.value = newOffset
  coinsStore.fetchCoins(limit.value, offset.value)
}

const exportCollection = async () => {
  const format = confirm('Экспорт в формате JSON? (Отмена - CSV)') ? 'json' : 'csv'
  window.open(`http://localhost:8000/api/coins/export/${format}`, '_blank')
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
  border-radius: 12px;
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
  border-radius: 24px;
  border: 1px solid #eef2f6;
}

.empty-icon {
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.empty-state p {
  color: #94a3b8;
  margin-bottom: 24px;
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
  border-radius: 10px;
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
</style>