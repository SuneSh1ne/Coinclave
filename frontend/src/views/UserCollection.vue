<template>
  <div class="user-page" v-if="user">
    <div class="user-header">
      <router-link to="/" class="back-link">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Назад
      </router-link>
      <div class="user-info">
        <div class="user-avatar">
          <span>{{ userInitial }}</span>
        </div>
        <div>
          <h1>{{ user.email }}</h1>
          <p class="user-stats">{{ userStats.coins_count || 0 }} монет • {{ formatPrice(userStats.total_value || 0) }} ₽</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Загрузка коллекции пользователя...</p>
    </div>

    <div v-else-if="coins.length === 0" class="empty-state">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      <h3>Коллекция пуста</h3>
      <p>У этого пользователя пока нет монет в коллекции</p>
    </div>

    <div v-else class="grid">
      <div v-for="coin in coins" :key="coin.id" class="user-coin-card" @click="showDetail(coin)">
        <div class="coin-image">
          <img v-if="coin.images && coin.images[0]" :src="getImageUrl(coin.images[0].image_path)" :alt="coin.name">
          <div v-else class="image-placeholder">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
            </svg>
          </div>
        </div>
        <div class="coin-info">
          <h3 class="coin-title">{{ coin.name }}</h3>
          <div class="coin-meta">
            <span>{{ coin.year }} г.</span>
            <span class="separator">•</span>
            <span>{{ coin.country }}</span>
          </div>
          <div class="coin-tags">
            <span class="tag">{{ getMetalName(coin.metal) }}</span>
            <span class="tag condition">{{ getConditionName(coin.condition) }}</span>
          </div>
          <div class="coin-value">{{ formatPrice(coin.estimated_value) }} ₽</div>
        </div>
      </div>
    </div>

    <!-- Модальное окно детального просмотра -->
    <div v-if="selectedCoin" class="modal-overlay" @click.self="selectedCoin = null">
      <div class="modal-container">
        <div class="modal-header">
          <h3>{{ selectedCoin.name }}</h3>
          <button class="modal-close" @click="selectedCoin = null">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-gallery">
            <div class="modal-main-image">
              <img v-if="modalCurrentImage" :src="getImageUrl(modalCurrentImage.image_path)" :alt="selectedCoin.name">
            </div>
            <div class="modal-thumbnails" v-if="selectedCoin.images && selectedCoin.images.length > 1">
              <div 
                v-for="img in selectedCoin.images" 
                :key="img.id" 
                class="modal-thumb"
                :class="{ active: modalCurrentImage?.id === img.id }"
                @click="modalCurrentImage = img"
              >
                <img :src="getImageUrl(img.image_path)" :alt="img.is_obverse ? 'Аверс' : 'Реверс'">
              </div>
            </div>
          </div>
          <div class="modal-info">
            <div class="info-row">
              <span class="info-label">Год чеканки</span>
              <span class="info-value">{{ selectedCoin.year }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Страна</span>
              <span class="info-value">{{ selectedCoin.country }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Номинал</span>
              <span class="info-value">{{ selectedCoin.denomination }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Металл</span>
              <span class="info-value">{{ getMetalName(selectedCoin.metal) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Состояние</span>
              <span class="info-value">
                <span class="condition-badge" :class="getConditionClass(selectedCoin.condition)">
                  {{ getConditionName(selectedCoin.condition) }}
                </span>
              </span>
            </div>
            <div class="info-row highlight">
              <span class="info-label">Оценочная стоимость</span>
              <span class="info-value">{{ formatPrice(selectedCoin.estimated_value) }} ₽</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading-page">
    <div class="loading-spinner"></div>
    <p>Загрузка...</p>
  </div>

  <div v-else class="not-found">
    <div class="not-found-content">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <h3>Пользователь не найден</h3>
      <router-link to="/" class="btn-primary">Вернуться в коллекцию</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const userStats = ref({})
const coins = ref([])
const loading = ref(true)
const selectedCoin = ref(null)
const modalCurrentImage = ref(null)

const userInitial = computed(() => {
  return user.value?.email ? user.value.email.charAt(0).toUpperCase() : 'U'
})

const getImageUrl = (path) => `http://localhost:8000/uploads/${path}`

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price || 0))
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
    poor: 'Poor', fair: 'Fair', good: 'Good', very_good: 'VG',
    fine: 'Fine', very_fine: 'VF', extremely_fine: 'XF', uncirculated: 'UNC'
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

const showDetail = (coin) => {
  selectedCoin.value = coin
  modalCurrentImage.value = coin.images?.[0] || null
}

onMounted(async () => {
  loading.value = true
  const userId = route.params.id
  
  try {
    const collectionRes = await api.get(`/users/${userId}/collection`)
    user.value = { email: collectionRes.data.user_email }
    coins.value = collectionRes.data.coins
    
    const statsRes = await api.get(`/users/${userId}/stats`)
    userStats.value = statsRes.data
  } catch (e) {
    if (e.response?.status === 404) {
      user.value = null
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.user-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

.user-header {
  margin-bottom: 32px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  margin-bottom: 20px;
  transition: color 0.2s;
}

.back-link:hover {
  color: #3b82f6;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 600;
  color: white;
}

.user-info h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.user-stats {
  font-size: 14px;
  color: #94a3b8;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.user-coin-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #eef2f6;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-coin-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.coin-image {
  height: 180px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.coin-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.coin-info {
  padding: 16px;
}

.coin-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.coin-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.separator {
  margin: 0 6px;
}

.coin-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
}

.tag.condition {
  background: #eff6ff;
  color: #3b82f6;
}

.coin-value {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.loading-state, .empty-state, .loading-page, .not-found {
  text-align: center;
  padding: 80px 40px;
  color: #94a3b8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

.empty-state h3, .not-found h3 {
  margin: 16px 0 8px;
  color: #64748b;
}

.not-found-content {
  text-align: center;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 24px;
  width: 800px;
  max-width: 90%;
  max-height: 85vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eef2f6;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #94a3b8;
}

.modal-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 24px;
}

.modal-gallery {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-main-image {
  background: #f8fafc;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-thumbnails {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.modal-thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.modal-thumb.active {
  border-color: #3b82f6;
}

.modal-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  margin: 0 -12px;
  padding: 12px;
  border-radius: 12px;
  border-bottom: none;
}

.info-row.highlight .info-value {
  font-size: 18px;
  font-weight: 700;
  color: #10b981;
}

.condition-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
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

@media (max-width: 640px) {
  .modal-body {
    grid-template-columns: 1fr;
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
  
  .user-avatar {
    width: 60px;
    height: 60px;
    font-size: 24px;
  }
}
</style>