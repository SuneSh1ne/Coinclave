<template>
  <div class="detail-page" v-if="coin">
    <div class="detail-container">
      <div class="detail-nav">
        <router-link to="/collection" class="back-link">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Назад к коллекции
        </router-link>
        <div class="action-buttons">
          <router-link :to="`/coin/${coin.id}/edit`" class="btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 3l4 4-7 7H10v-4l7-7z"/>
              <path d="M4 20h16"/>
            </svg>
            Редактировать
          </router-link>
          <button @click="deleteCoin" class="btn-danger">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 7h16M10 11v6M14 11v6M5 7l1 13a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-13M9 3h6v4H9z"/>
            </svg>
            Удалить
          </button>
        </div>
      </div>

      <div class="detail-content">
        <div class="detail-gallery">
          <div class="main-image">
            <img v-if="currentImage" :src="getImageUrl(currentImage.image_path)" :alt="coin.name">
            <div v-else class="no-image">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                <circle cx="8.5" cy="8.5" r="2.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
          </div>
          <div class="thumbnail-list" v-if="coin.images && coin.images.length > 1">
            <div 
              v-for="img in coin.images" 
              :key="img.id" 
              class="thumbnail"
              :class="{ active: currentImage?.id === img.id }"
              @click="currentImage = img"
            >
              <img :src="getImageUrl(img.image_path)" :alt="img.is_obverse ? 'Аверс' : 'Реверс'">
              <span class="thumbnail-label">{{ img.is_obverse ? 'Аверс' : 'Реверс' }}</span>
            </div>
          </div>
        </div>

        <div class="detail-info">
          <h1 class="coin-name">{{ coin.name }}</h1>
          
          <div class="info-grid">
            <div class="info-row">
              <div class="info-label">Год чеканки</div>
              <div class="info-value">{{ coin.year }}</div>
            </div>
            <div class="info-row">
              <div class="info-label">Страна</div>
              <div class="info-value">{{ coin.country }}</div>
            </div>
            <div class="info-row">
              <div class="info-label">Номинал</div>
              <div class="info-value">{{ coin.denomination }}</div>
            </div>
            <div class="info-row">
              <div class="info-label">Металл</div>
              <div class="info-value">{{ getMetalName(coin.metal) }}</div>
            </div>
            <div class="info-row">
              <div class="info-label">Состояние</div>
              <div class="info-value">
                <span class="condition-badge" :class="getConditionClass(coin.condition)">
                  {{ getConditionName(coin.condition) }}
                </span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-label">Цена покупки</div>
              <div class="info-value">{{ coin.purchase_price ? formatPrice(coin.purchase_price) + ' ₽' : '—' }}</div>
            </div>
            <div class="info-row highlight">
              <div class="info-label">Оценочная стоимость</div>
              <div class="info-value">{{ formatPrice(coin.estimated_value) }} ₽</div>
            </div>
          </div>

          <div v-if="isOnExchange" class="exchange-status">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 2l4 4-4 4M3 12h15M7 2l-4 4 4 4"/>
              <path d="M21 12h-15M17 22l4-4-4-4"/>
            </svg>
            <span>Эта монета доступна для обмена</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else-if="loading" class="loading-page">
    <div class="loading-spinner"></div>
    <p>Загрузка информации о монете...</p>
  </div>
  
  <div v-else class="not-found">
    <div class="not-found-content">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="none" stroke="#ef4444" stroke-width="2"/>
        <rect x="10.5" y="6" width="3" height="9" rx="1.5" fill="#ef4444"/>
        <circle cx="12" cy="18" r="1.5" fill="#ef4444"/>
      </svg>
      <h3>Монета не найдена</h3>
      <router-link to="/collection" class="btn-primary">Вернуться в коллекцию</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const coin = ref(null)
const loading = ref(true)
const currentImage = ref(null)
const isOnExchange = ref(false)

const getImageUrl = (path) => `http://localhost:8000/uploads/${path}`

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price))
}

const getMetalName = (metal) => {
  const metals = {
    gold: 'Золото', silver: 'Серебро', copper: 'Медь', nickel: 'Никель',
    brass: 'Латунь', bronze: 'Бронза', aluminum: 'Алюминий', bimetallic: 'Биметалл'
  }
  return metals[metal] || metal
}

const getConditionName = (condition) => {
  const conditions = {
    poor: 'Poor', fair: 'Fair', good: 'Good', very_good: 'Very Good',
    fine: 'Fine', very_fine: 'Very Fine', extremely_fine: 'Extremely Fine',
    uncirculated: 'Uncirculated'
  }
  return conditions[condition] || condition
}

const getConditionClass = (condition) => {
  const classes = {
    poor: 'condition-poor', fair: 'condition-fair', good: 'condition-good',
    very_good: 'condition-vg', fine: 'condition-fine', very_fine: 'condition-vf',
    extremely_fine: 'condition-xf', uncirculated: 'condition-unc'
  }
  return classes[condition] || ''
}

const checkExchangeStatus = async () => {
  try {
    const res = await api.get('/exchange/listings')
    isOnExchange.value = res.data.items.some(item => item.id === coin.value.id)
  } catch (e) {}
}

const deleteCoin = async () => {
  if (confirm('Вы уверены, что хотите удалить эту монету? Данные будут потеряны.')) {
    try {
      await api.delete(`/api/coins/${coin.value.id}`)
      router.push('/collection')
    } catch (e) {
      alert('Ошибка при удалении')
    }
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/coins/${route.params.id}`)
    coin.value = res.data
    if (coin.value.images && coin.value.images.length > 0) {
      currentImage.value = coin.value.images[0]
    }
    await checkExchangeStatus()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.detail-container {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid #eef2f6;
}

.detail-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1px solid #eef2f6;
  flex-wrap: wrap;
  gap: 16px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 30px;
  transition: all 0.2s;
}

.back-link:hover {
  background: #f1f5f9;
  color: #3b82f6;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-secondary, .btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  padding: 32px 28px;
}

.detail-gallery {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.main-image {
  aspect-ratio: 1 / 1;
  background: #f8fafc;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-image svg {
  stroke: #cbd5e1;
}

.thumbnail-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.thumbnail {
  width: 80px;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.2s;
  position: relative;
}

.thumbnail.active {
  border-color: #3b82f6;
}

.thumbnail img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
}

.thumbnail-label {
  position: absolute;
  bottom: 4px;
  left: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
}

.coin-name {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f6;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 28px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-label {
  font-size: 13px;
  color: #94a3b8;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.info-row.highlight {
  background: #f8fafc;
  margin: 8px -12px;
  padding: 12px;
  border-radius: 12px;
  border-bottom: none;
}

.info-row.highlight .info-label {
  font-weight: 600;
  color: #475569;
}

.info-row.highlight .info-value {
  font-size: 18px;
  font-weight: 700;
  color: #10b981;
}

.condition-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 500;
}

.condition-poor { background: #fef2f2; color: #ef4444; }
.condition-fair { background: #fffbeb; color: #f59e0b; }
.condition-good { background: #eff6ff; color: #3b82f6; }
.condition-vg { background: #e0f2fe; color: #0ea5e9; }
.condition-fine { background: #ecfdf5; color: #10b981; }
.condition-vf { background: #ecfdf5; color: #10b981; }
.condition-xf { background: #fef3c7; color: #d97706; }
.condition-unc { background: #fef3c7; color: #d97706; }

.exchange-status {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eef2f6;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #10b981;
}

.loading-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
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

.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.not-found-content {
  text-align: center;
  padding: 48px;
}

.not-found-content svg {
  margin-bottom: 20px;
}

.not-found-content h3 {
  margin: 16px 0 24px;
  color: #64748b;
  font-size: 18px;
  font-weight: 600;
}

.not-found-content .btn-primary {
  border-radius: 30px;
  padding: 10px 28px;
  text-decoration: none;
  display: inline-block;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.not-found-content .btn-primary:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
}

/* Тёмная тема */
body.dark-theme .detail-container {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .detail-nav {
  border-color: #334155;
}

body.dark-theme .back-link {
  color: #94a3b8;
}

body.dark-theme .back-link:hover {
  background: #334155;
  color: #3b82f6;
}

body.dark-theme .coin-name {
  color: #f1f5f9;
  border-color: #334155;
}

body.dark-theme .info-row {
  border-color: #334155;
}

body.dark-theme .info-label {
  color: #94a3b8;
}

body.dark-theme .info-value {
  color: #f1f5f9;
}

body.dark-theme .info-row.highlight {
  background: #0f172a;
}

body.dark-theme .main-image {
  background: #0f172a;
}

body.dark-theme .no-image svg {
  stroke: #475569;
}

body.dark-theme .exchange-status {
  border-color: #334155;
}

body.dark-theme .not-found-content h3 {
  color: #94a3b8;
}

@media (max-width: 768px) {
  .detail-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .coin-name {
    font-size: 24px;
  }
}
</style>