<template>
  <div class="exchange-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Обмен монетами</h1>
        <p class="page-subtitle">Находите интересные экземпляры и предлагайте обмен другим коллекционерам</p>
      </div>
    </div>

    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-btn" 
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span v-if="tab.key === 'received' && pendingOffersCount > 0" class="tab-badge">{{ pendingOffersCount }}</span>
      </button>
    </div>

    <!-- Вкладка: Доступные для обмена -->
    <div v-if="activeTab === 'available'" class="tab-content">
      <div class="filter-bar">
        <div class="filter-group">
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Поиск по названию..."
            @input="debouncedFetchListings"
            class="filter-input"
          >
        </div>
        <div class="filter-group">
          <select v-model="filters.country" @change="fetchListings" class="filter-select">
            <option value="">Все страны</option>
            <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="filters.metal" @change="fetchListings" class="filter-select">
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
          <select v-model="filters.condition" @change="fetchListings" class="filter-select">
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
        <button class="btn-secondary reset-btn" @click="resetFilters">Сбросить</button>
      </div>

      <div v-if="listingsLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка доступных монет...</p>
      </div>

      <div v-else-if="listings.length === 0" class="empty-state">
        <p>Нет монет, доступных для обмена</p>
      </div>

      <div v-else class="listings-grid">
        <div v-for="item in listings" :key="item.id" class="listing-card">
          <div class="listing-image">
            <img v-if="item.images && item.images[0]" :src="getImageUrl(item.images[0].image_path)" :alt="item.name">
            <div v-else class="image-placeholder">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
              </svg>
            </div>
          </div>
          <div class="listing-info">
            <h3 class="listing-title">{{ item.name }}</h3>
            <div class="listing-meta">
              <span>{{ item.year }} г.</span>
              <span class="separator">•</span>
              <span>{{ item.country }}</span>
            </div>
            <div class="listing-tags">
              <span class="tag">{{ getMetalName(item.metal) }}</span>
              <span class="tag condition">{{ getConditionName(item.condition) }}</span>
            </div>
            <div class="listing-footer">
              <span class="owner">Владелец: {{ item.owner_email }}</span>
              <span class="value">{{ formatPrice(item.estimated_value) }} ₽</span>
            </div>
            <button class="btn-exchange" @click="openOfferModal(item)">Предложить обмен</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Вкладка: Мои монеты на обмене -->
    <div v-if="activeTab === 'myListings'" class="tab-content">
      <div v-if="myListingsLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>

      <div v-else-if="myListings.length === 0" class="empty-state">
        <p>Вы не выставили ни одной монеты на обмен</p>
        <router-link to="/" class="btn-outline">Перейти к коллекции</router-link>
      </div>

      <div v-else class="listings-grid">
        <div v-for="item in myListings" :key="item.id" class="listing-card my-listing">
          <div class="listing-image">
            <img v-if="item.images && item.images[0]" :src="getImageUrl(item.images[0].image_path)" :alt="item.name">
            <div v-else class="image-placeholder">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
              </svg>
            </div>
          </div>
          <div class="listing-info">
            <h3 class="listing-title">{{ item.name }}</h3>
            <div class="listing-meta">
              <span>{{ item.year }} г.</span>
              <span class="separator">•</span>
              <span>{{ item.country }}</span>
            </div>
            <div class="listing-footer">
              <span class="value">{{ formatPrice(item.estimated_value) }} ₽</span>
            </div>
            <button class="btn-danger" @click="removeFromExchange(item.id)">Снять с обмена</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Вкладка: Исходящие предложения -->
    <div v-if="activeTab === 'sent'" class="tab-content">
      <div v-if="sentOffersLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>

      <div v-else-if="sentOffers.length === 0" class="empty-state">
        <p>Нет отправленных предложений</p>
      </div>

      <div v-else class="offers-list">
        <div v-for="offer in sentOffers" :key="offer.id" class="offer-card" :class="offer.status">
          <div class="offer-status">
            <span class="status-badge" :class="offer.status">
              {{ getOfferStatus(offer.status) }}
            </span>
          </div>
          <div class="offer-details">
            <div class="offer-coins">
              <div class="offer-coin">
                <span class="offer-label">Предлагается:</span>
                <span class="offer-value">{{ offer.offered_coin?.name || 'Монета' }}</span>
              </div>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
              <div class="offer-coin">
                <span class="offer-label">Запрашивается:</span>
                <span class="offer-value">{{ offer.requested_coin?.name || 'Монета' }}</span>
              </div>
            </div>
            <div class="offer-meta">
              <span class="offer-date">{{ formatDate(offer.created_at) }}</span>
            </div>
          </div>
          <div v-if="offer.status === 'pending'" class="offer-actions">
            <button class="btn-secondary" @click="cancelOffer(offer.id)">Отменить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Вкладка: Входящие предложения -->
    <div v-if="activeTab === 'received'" class="tab-content">
      <div v-if="receivedOffersLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>

      <div v-else-if="receivedOffers.length === 0" class="empty-state">
        <p>Нет входящих предложений</p>
      </div>

      <div v-else class="offers-list">
        <div v-for="offer in receivedOffers" :key="offer.id" class="offer-card" :class="offer.status">
          <div class="offer-status">
            <span class="status-badge" :class="offer.status">
              {{ getOfferStatus(offer.status) }}
            </span>
          </div>
          <div class="offer-details">
            <div class="offer-coins">
              <div class="offer-coin">
                <span class="offer-label">Предлагается:</span>
                <span class="offer-value">{{ offer.offered_coin?.name || 'Монета' }}</span>
              </div>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
              <div class="offer-coin">
                <span class="offer-label">За вашу:</span>
                <span class="offer-value">{{ offer.requested_coin?.name || 'Монета' }}</span>
              </div>
            </div>
            <div class="offer-meta">
              <span class="offer-date">{{ formatDate(offer.created_at) }}</span>
            </div>
          </div>
          <div v-if="offer.status === 'pending'" class="offer-actions">
            <button class="btn-success" @click="acceptOffer(offer.id)">Принять</button>
            <button class="btn-danger" @click="rejectOffer(offer.id)">Отклонить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно предложения обмена -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Новое предложение обмена</h3>
          <button class="modal-close" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="exchange-details">
            <div class="target-coin">
              <span class="label">Запрашиваемая монета:</span>
              <div class="coin-info">
                <strong>{{ selectedCoin?.name }}</strong>
                <span>{{ selectedCoin?.year }} г., {{ selectedCoin?.country }}</span>
                <span class="value">{{ formatPrice(selectedCoin?.estimated_value) }} ₽</span>
              </div>
            </div>

            <div class="form-group">
              <label>Выберите свою монету для обмена</label>
              <select v-model="selectedMyCoinId" class="form-select">
                <option value="">-- Выберите монету --</option>
                <option v-for="coin in myCoins" :key="coin.id" :value="coin.id">
                  {{ coin.name }} ({{ coin.year }} г.) - {{ formatPrice(coin.estimated_value) }} ₽
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Сообщение (необязательно)</label>
              <textarea v-model="offerMessage" class="form-textarea" rows="3" placeholder="Добавьте комментарий к предложению..."></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showModal = false">Отмена</button>
          <button class="btn-primary" @click="sendOffer" :disabled="!selectedMyCoinId">Отправить предложение</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const activeTab = ref('available')
const tabs = [
  { key: 'available', label: 'Доступные для обмена' },
  { key: 'myListings', label: 'Мои на обмене' },
  { key: 'sent', label: 'Исходящие' },
  { key: 'received', label: 'Входящие' }
]

const listings = ref([])
const myListings = ref([])
const sentOffers = ref([])
const receivedOffers = ref([])
const myCoins = ref([])

const listingsLoading = ref(false)
const myListingsLoading = ref(false)
const sentOffersLoading = ref(false)
const receivedOffersLoading = ref(false)

const showModal = ref(false)
const selectedCoin = ref(null)
const selectedMyCoinId = ref('')
const offerMessage = ref('')
const countries = ref([])

const filters = ref({
  search: '',
  country: '',
  metal: '',
  condition: ''
})

let debounceTimer = null
const debouncedFetchListings = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchListings()
  }, 300)
}

const pendingOffersCount = computed(() => {
  return receivedOffers.value.filter(o => o.status === 'pending').length
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price || 0))
}

const getImageUrl = (path) => `http://localhost:8000/uploads/${path}`

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

const getOfferStatus = (status) => {
  const statuses = {
    pending: 'Ожидает',
    accepted: 'Принято',
    rejected: 'Отклонено',
    cancelled: 'Отменено'
  }
  return statuses[status] || status
}

const formatDate = (date) => {
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'только что'
  if (minutes < 60) return `${minutes} мин назад`
  if (minutes < 1440) return `${Math.floor(minutes / 60)} ч назад`
  return `${Math.floor(minutes / 1440)} д назад`
}

const fetchListings = async () => {
  listingsLoading.value = true
  try {
    const params = { ...filters.value }
    Object.keys(params).forEach(k => !params[k] && delete params[k])
    const res = await api.get('/exchange/listings', { params })
    listings.value = res.data.items
  } catch (e) {}
  listingsLoading.value = false
}

const fetchMyListings = async () => {
  myListingsLoading.value = true
  try {
    const res = await api.get('/api/coins')
    const allCoins = res.data.items
    const exchangeRes = await api.get('/exchange/listings')
    const exchangeIds = exchangeRes.data.items.map(i => i.id)
    myListings.value = allCoins.filter(c => exchangeIds.includes(c.id))
  } catch (e) {}
  myListingsLoading.value = false
}

const fetchOffers = async () => {
  sentOffersLoading.value = true
  receivedOffersLoading.value = true
  
  try {
    const sentRes = await api.get('/exchange/offers/sent')
    sentOffers.value = sentRes.data
  } catch (e) {}
  sentOffersLoading.value = false
  
  try {
    const receivedRes = await api.get('/exchange/offers/received')
    receivedOffers.value = receivedRes.data
  } catch (e) {}
  receivedOffersLoading.value = false
}

const fetchMyCoins = async () => {
  try {
    const res = await api.get('/api/coins')
    myCoins.value = res.data.items.filter(c => c.id !== selectedCoin.value?.id)
  } catch (e) {}
}

const fetchCountries = async () => {
  try {
    const res = await api.get('/api/coins/filters/countries')
    countries.value = res.data.countries
  } catch (e) {}
}

const resetFilters = () => {
  filters.value = { search: '', country: '', metal: '', condition: '' }
  fetchListings()
}

const openOfferModal = (coin) => {
  selectedCoin.value = coin
  selectedMyCoinId.value = ''
  offerMessage.value = ''
  fetchMyCoins().then(() => {
    showModal.value = true
  })
}

const sendOffer = async () => {
  if (!selectedMyCoinId.value) return
  
  try {
    await api.post('/exchange/offers', {
      offered_coin_id: selectedMyCoinId.value,
      requested_coin_id: selectedCoin.value.id,
      message: offerMessage.value
    })
    showModal.value = false
    fetchOffers()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при отправке предложения')
  }
}

const removeFromExchange = async (coinId) => {
  try {
    await api.delete(`/exchange/listings/${coinId}`)
    await fetchMyListings()
    await fetchListings()
  } catch (e) {
    alert('Ошибка')
  }
}

const acceptOffer = async (offerId) => {
  if (confirm('Принять предложение? После подтверждения монеты будут обменяны.')) {
    try {
      await api.put(`/exchange/offers/${offerId}/accept`)
      await fetchOffers()
      await fetchMyListings()
      await fetchListings()
    } catch (e) {
      alert('Ошибка при принятии предложения')
    }
  }
}

const rejectOffer = async (offerId) => {
  try {
    await api.put(`/exchange/offers/${offerId}/reject`)
    await fetchOffers()
  } catch (e) {
    alert('Ошибка')
  }
}

const cancelOffer = async (offerId) => {
  try {
    await api.put(`/exchange/offers/${offerId}/cancel`)
    await fetchOffers()
  } catch (e) {
    alert('Ошибка')
  }
}

onMounted(() => {
  fetchListings()
  fetchMyListings()
  fetchOffers()
  fetchCountries()
})
</script>

<style scoped>
.exchange-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  margin-bottom: 32px;
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

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 28px;
  border-bottom: 1px solid #eef2f6;
  padding-bottom: 0;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tab-btn:hover {
  color: #3b82f6;
}

.tab-btn.active {
  color: #3b82f6;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}

.tab-badge {
  display: inline-block;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 20px;
  margin-left: 6px;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  flex: 1;
  min-width: 150px;
}

.filter-input,
.filter-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
}

.reset-btn {
  padding: 8px 20px;
}

.listings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.listing-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #eef2f6;
  overflow: hidden;
  transition: all 0.2s ease;
}

.listing-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.listing-image {
  height: 160px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.listing-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.listing-info {
  padding: 16px;
}

.listing-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.listing-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.separator {
  margin: 0 6px;
}

.listing-tags {
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

.listing-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  font-size: 12px;
}

.owner {
  color: #94a3b8;
}

.value {
  font-weight: 600;
  color: #1e293b;
}

.btn-exchange {
  width: 100%;
  padding: 8px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-exchange:hover {
  background: #059669;
}

.my-listing {
  border-left: 3px solid #10b981;
}

.offers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.offer-card {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  border: 1px solid #eef2f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.offer-card.pending {
  border-left: 3px solid #f59e0b;
}

.offer-card.accepted {
  border-left: 3px solid #10b981;
}

.offer-card.rejected,
.offer-card.cancelled {
  border-left: 3px solid #ef4444;
  opacity: 0.7;
}

.status-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.accepted {
  background: #ecfdf5;
  color: #059669;
}

.status-badge.rejected,
.status-badge.cancelled {
  background: #fef2f2;
  color: #dc2626;
}

.offer-details {
  flex: 1;
}

.offer-coins {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.offer-coin {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.offer-label {
  color: #94a3b8;
}

.offer-value {
  font-weight: 500;
  color: #1e293b;
}

.offer-meta {
  font-size: 11px;
  color: #cbd5e1;
}

.offer-actions {
  display: flex;
  gap: 10px;
}

.btn-success {
  background: #10b981;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #94a3b8;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-bottom: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #94a3b8;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 500px;
  max-width: 90%;
  overflow: hidden;
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
  font-size: 24px;
  cursor: pointer;
  color: #94a3b8;
}

.modal-body {
  padding: 24px;
}

.exchange-details {
  margin-bottom: 20px;
}

.target-coin {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 20px;
}

.target-coin .label {
  font-size: 12px;
  color: #94a3b8;
  display: block;
  margin-bottom: 8px;
}

.coin-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.coin-info strong {
  font-size: 16px;
  color: #1e293b;
}

.coin-info .value {
  color: #10b981;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eef2f6;
}
</style>