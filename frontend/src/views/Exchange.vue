<template>
  <div class="exchange-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Обмен монетами</h1>
        <p class="page-subtitle">Управление предложениями обмена с другими коллекционерами</p>
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

    <!-- Исходящие предложения -->
    <div v-if="activeTab === 'sent'" class="tab-content">
      <div v-if="sentOffersLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>

      <div v-else-if="sentOffers.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="none" stroke="#94a3b8" stroke-width="2"/>
          <rect x="10.5" y="6" width="3" height="9" rx="1.5" fill="#94a3b8"/>
          <circle cx="12" cy="18" r="1.5" fill="#94a3b8"/>
        </svg>
        <p>Нет отправленных предложений</p>
      </div>

      <div v-else class="offers-list">
        <div v-for="offer in sentOffers" :key="offer.id" class="offer-card" :class="offer.status" @click="openOfferDetail(offer)">
          <div class="offer-status">
            <span class="status-badge" :class="offer.status">
              {{ getOfferStatus(offer.status) }}
            </span>
          </div>
          <div class="offer-details">
            <div class="offer-coins">
              <div class="offer-coin">
                <span class="offer-label">Предлагается:</span>
                <span class="offer-value">{{ getCoinsList(offer.offered_coins) }}</span>
              </div>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
              <div class="offer-coin">
                <span class="offer-label">Запрашивается:</span>
                <span class="offer-value">{{ getCoinsList(offer.requested_coins) }}</span>
              </div>
            </div>
            <div class="offer-meta">
              <span class="offer-date">{{ formatDate(offer.created_at) }}</span>
              <span v-if="offer.message" class="offer-message">💬 {{ offer.message }}</span>
            </div>
          </div>
          <div v-if="offer.status === 'pending'" class="offer-actions">
            <button class="btn-secondary" @click.stop="cancelOffer(offer.id)">Отменить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Входящие предложения -->
    <div v-if="activeTab === 'received'" class="tab-content">
      <div class="filter-bar">
        <div class="filter-header">
          <h3 class="filter-title">Фильтрация предложений</h3>
          <button @click="resetFilters" class="reset-btn">Сбросить все</button>
        </div>
        
        <div class="filters-grid">
          <div class="filter-group">
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="Поиск по монете..."
              @input="debouncedFilterOffers"
              class="filter-input"
            >
          </div>
          
          <div class="filter-group">
            <select v-model="filters.status" @change="filterOffers" class="filter-select">
              <option value="">Все статусы</option>
              <option value="pending">Ожидает</option>
              <option value="accepted">Принято</option>
              <option value="rejected">Отклонено</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="receivedOffersLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка...</p>
      </div>

      <div v-else-if="filteredReceivedOffers.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="none" stroke="#94a3b8" stroke-width="2"/>
          <rect x="10.5" y="6" width="3" height="9" rx="1.5" fill="#94a3b8"/>
          <circle cx="12" cy="18" r="1.5" fill="#94a3b8"/>
        </svg>
        <p>Нет входящих предложений</p>
      </div>

      <div v-else class="offers-list">
        <div v-for="offer in filteredReceivedOffers" :key="offer.id" class="offer-card" :class="offer.status" @click="openOfferDetail(offer)">
          <div class="offer-status">
            <span class="status-badge" :class="offer.status">
              {{ getOfferStatus(offer.status) }}
            </span>
          </div>
          <div class="offer-details">
            <div class="offer-coins">
              <div class="offer-coin">
                <span class="offer-label">Предлагается:</span>
                <span class="offer-value">{{ getCoinsList(offer.offered_coins) }}</span>
              </div>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
              <div class="offer-coin">
                <span class="offer-label">За вашу:</span>
                <span class="offer-value">{{ getCoinsList(offer.requested_coins) }}</span>
              </div>
            </div>
            <div class="offer-meta">
              <span class="offer-date">{{ formatDate(offer.created_at) }}</span>
              <span v-if="offer.message" class="offer-message">💬 {{ offer.message }}</span>
            </div>
          </div>
          <div v-if="offer.status === 'pending'" class="offer-actions">
            <button class="btn-success" @click.stop="acceptOffer(offer.id)">Принять</button>
            <button class="btn-danger" @click.stop="rejectOffer(offer.id)">Отклонить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно деталей обмена -->
    <div v-if="showOfferDetailModal && selectedOffer" class="modal-overlay" @click.self="closeOfferDetail">
      <div class="modal-container modal-offer-detail">
        <div class="modal-header">
          <h3>Детали предложения обмена</h3>
          <button class="modal-close" @click="closeOfferDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="offer-detail-section">
            <h4>Информация о предложении</h4>
            <div class="detail-row">
              <span class="detail-label">Статус:</span>
              <span class="status-badge" :class="selectedOffer.status">
                {{ getOfferStatus(selectedOffer.status) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Дата создания:</span>
              <span class="detail-value">{{ formatDate(selectedOffer.created_at) }}</span>
            </div>
            <div v-if="selectedOffer.message" class="detail-row">
              <span class="detail-label">Сообщение:</span>
              <span class="detail-value message-text">{{ selectedOffer.message }}</span>
            </div>
          </div>

          <div class="offer-detail-section">
            <h4>Что предлагает отправитель</h4>
            <div v-if="selectedOffer.offered_coins && selectedOffer.offered_coins.length > 0" class="coins-detail-list">
              <div v-for="coin in selectedOffer.offered_coins" :key="coin.id" class="coin-detail-item">
                <div class="coin-detail-image">
                  <img v-if="coin.images && coin.images[0] && coin.images[0].image_path" 
                      :src="getImageUrl(coin.images[0].image_path)" 
                      :alt="coin.name">
                  <div v-else class="small-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                      <circle cx="8.5" cy="8.5" r="2.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                  </div>
                </div>
                <div class="coin-detail-info">
                  <div class="coin-detail-name">{{ coin.name }}</div>
                  <div class="coin-detail-meta">{{ coin.year }} г., {{ coin.country }}</div>
                  <div class="coin-detail-value">{{ formatPrice(coin.estimated_value) }} ₽</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-coins-message">
              <p>Ничего не предлагается</p>
            </div>
          </div>

          <div class="offer-detail-section">
            <h4>Что запрашивает отправитель</h4>
            <div v-if="selectedOffer.requested_coins && selectedOffer.requested_coins.length > 0" class="coins-detail-list">
              <div v-for="coin in selectedOffer.requested_coins" :key="coin.id" class="coin-detail-item">
                <div class="coin-detail-image">
                  <img v-if="coin.images && coin.images[0] && coin.images[0].image_path" 
                    :src="getImageUrl(coin.images[0].image_path)" 
                    :alt="coin.name">
                  <div v-else class="small-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                      <circle cx="8.5" cy="8.5" r="2.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                  </div>
                </div>
                <div class="coin-detail-info">
                  <div class="coin-detail-name">{{ coin.name }}</div>
                  <div class="coin-detail-meta">{{ coin.year }} г., {{ coin.country }}</div>
                  <div class="coin-detail-value">{{ formatPrice(coin.estimated_value) }} ₽</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-coins-message">
              <p>Ничего не запрашивается</p>
            </div>
          </div>

          <div class="offer-detail-section summary">
            <div class="summary-row">
              <span>Итого отдаётся:</span>
              <span class="summary-value">{{ formatPrice(calculateTotal(selectedOffer.offered_coins)) }} ₽</span>
            </div>
            <div class="summary-row">
              <span>Итого получается:</span>
              <span class="summary-value">{{ formatPrice(calculateTotal(selectedOffer.requested_coins)) }} ₽</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-row total">
              <span>Разница:</span>
              <span class="summary-value">{{ formatPrice(Math.abs(calculateTotal(selectedOffer.offered_coins) - calculateTotal(selectedOffer.requested_coins))) }} ₽</span>
            </div>
          </div>

          <div v-if="activeTab === 'received' && selectedOffer.status === 'pending'" class="modal-actions">
            <button class="btn-success" @click="acceptOfferFromModal">Принять предложение</button>
            <button class="btn-danger" @click="rejectOfferFromModal">Отклонить предложение</button>
          </div>

          <div v-if="activeTab === 'sent' && selectedOffer.status === 'pending'" class="modal-actions">
            <button class="btn-danger" @click="cancelOfferFromModal">Отменить предложение</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const authStore = useAuthStore()
const activeTab = ref('received')
const tabs = [
  { key: 'received', label: 'Входящие предложения' },
  { key: 'sent', label: 'Исходящие предложения' }
]

const sentOffers = ref([])
const receivedOffers = ref([])

const sentOffersLoading = ref(false)
const receivedOffersLoading = ref(false)

const showOfferDetailModal = ref(false)
const selectedOffer = ref(null)

const filters = ref({
  search: '',
  status: ''
})

let debounceTimer = null
const debouncedFilterOffers = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    filterOffers()
  }, 300)
}

const filteredReceivedOffers = computed(() => {
  let result = [...receivedOffers.value]
  
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    result = result.filter(offer => {
      const offeredNames = offer.offered_coins?.map(c => c.name.toLowerCase()).join(' ') || ''
      const requestedNames = offer.requested_coins?.map(c => c.name.toLowerCase()).join(' ') || ''
      return offeredNames.includes(searchLower) || requestedNames.includes(searchLower)
    })
  }
  
  if (filters.value.status) {
    result = result.filter(offer => offer.status === filters.value.status)
  }
  
  return result
})

const filterOffers = () => {}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
}

const pendingOffersCount = computed(() => {
  return receivedOffers.value.filter(o => o.status === 'pending').length
})

const getImageUrl = (path) => {
  if (!path) return ''
  return `http://localhost:8000/uploads/${path}`
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price || 0))
}

const getCoinsList = (coins) => {
  if (!coins || coins.length === 0) return 'Ничего'
  const validCoins = coins.filter(c => c && c.id)
  if (validCoins.length === 0) return 'Ничего'
  if (validCoins.length === 1) {
    const coin = validCoins[0]
    return `${coin.name} (${coin.year}) - ${formatPrice(coin.estimated_value)} ₽`
  }
  const totalValue = validCoins.reduce((sum, c) => sum + (c.estimated_value || 0), 0)
  return `${validCoins.length} монет (${formatPrice(totalValue)} ₽)`
}

const calculateTotal = (coins) => {
  if (!coins || coins.length === 0) return 0
  return coins.reduce((sum, c) => sum + (c.estimated_value || 0), 0)
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
  const diffMs = now - d
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffSeconds < 60) {
    return 'только что'
  } else if (diffMinutes < 60) {
    const minutes = diffMinutes
    if (minutes === 1) return '1 минуту назад'
    if (minutes >= 2 && minutes <= 4) return `${minutes} минуты назад`
    return `${minutes} минут назад`
  } else if (diffHours < 24) {
    const hours = diffHours
    if (hours === 1) return '1 час назад'
    if (hours >= 2 && hours <= 4) return `${hours} часа назад`
    return `${hours} часов назад`
  } else if (diffDays < 30) {
    const days = diffDays
    if (days === 1) return '1 день назад'
    if (days >= 2 && days <= 4) return `${days} дня назад`
    return `${days} дней назад`
  } else {
    return 'более 30 дней назад'
  }
}

const fetchSentOffers = async () => {
  sentOffersLoading.value = true
  try {
    const res = await api.get('/exchange/offers/sent')
    sentOffers.value = res.data
  } catch (e) {}
  sentOffersLoading.value = false
}

const fetchReceivedOffers = async () => {
  receivedOffersLoading.value = true
  try {
    const res = await api.get('/exchange/offers/received')
    receivedOffers.value = res.data
  } catch (e) {}
  receivedOffersLoading.value = false
}

const openOfferDetail = (offer) => {
  selectedOffer.value = offer
  showOfferDetailModal.value = true
  document.body.classList.add('modal-open')
}

const closeOfferDetail = () => {
  showOfferDetailModal.value = false
  selectedOffer.value = null
  document.body.classList.remove('modal-open')
}

const acceptOffer = async (offerId) => {
  if (confirm('Принять предложение? После подтверждения монеты будут обменяны.')) {
    try {
      const response = await api.put(`/exchange/offers/${offerId}/accept`)
      await fetchReceivedOffers()
      await fetchSentOffers()
      await authStore.fetchUnreadCount()
    } catch (e) {
      alert(e.response?.data?.detail || 'Ошибка при принятии предложения')
    }
  }
}

const rejectOffer = async (offerId) => {
  try {
    const response = await api.put(`/exchange/offers/${offerId}/reject`)
    await fetchReceivedOffers()
    await fetchSentOffers()
    await authStore.fetchUnreadCount()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при отклонении предложения')
  }
}

const acceptOfferFromModal = async () => {
  if (selectedOffer.value) {
    await acceptOffer(selectedOffer.value.id)
    closeOfferDetail()
  }
}

const rejectOfferFromModal = async () => {
  if (selectedOffer.value) {
    await rejectOffer(selectedOffer.value.id)
    closeOfferDetail()
  }
}

const cancelOfferFromModal = async () => {
  if (selectedOffer.value) {
    await cancelOffer(selectedOffer.value.id)
    closeOfferDetail()
  }
}

const cancelOffer = async (offerId) => {
  try {
    const response = await api.put(`/exchange/offers/${offerId}/cancel`)
    await fetchSentOffers()
    await fetchReceivedOffers()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

onMounted(() => {
  fetchSentOffers()
  fetchReceivedOffers()
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
  border-radius: 30px;
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
  cursor: pointer;
  transition: all 0.2s;
}

.offer-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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
  flex-wrap: wrap;
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
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.offer-date {
  font-size: 11px;
  color: #cbd5e1;
}

.offer-message {
  font-size: 11px;
  color: #3b82f6;
  background: #eff6ff;
  padding: 2px 8px;
  border-radius: 12px;
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
  border-radius: 30px;
  cursor: pointer;
  font-size: 12px;
}

.btn-success:hover {
  background: #059669;
}

.btn-danger {
  background: #ef4444;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 12px;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-secondary {
  background: #f1f5f9;
  border: none;
  padding: 6px 16px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 12px;
}

.btn-secondary:hover {
  background: #e2e8f0;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #94a3b8;
}

.empty-state svg {
  margin-bottom: 16px;
}

/* Модальное окно деталей */
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
  max-width: 90%;
  max-height: 85vh;
  overflow: auto;
}

.modal-offer-detail {
  width: 700px;
  max-width: 95%;
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
  border-radius: 30px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f1f5f9;
}

.modal-body {
  padding: 24px;
}

.offer-detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f6;
}

.offer-detail-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  margin-bottom: 12px;
}

.detail-label {
  width: 120px;
  font-size: 13px;
  color: #94a3b8;
}

.detail-value {
  flex: 1;
  font-size: 13px;
  color: #1e293b;
}

.message-text {
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
}

.coins-detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coin-detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.coin-detail-image {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coin-detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.small-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.coin-detail-info {
  flex: 1;
}

.coin-detail-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.coin-detail-meta {
  font-size: 11px;
  color: #94a3b8;
}

.coin-detail-value {
  font-size: 12px;
  font-weight: 600;
  color: #10b981;
}

.empty-coins-message {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 13px;
}

.offer-detail-section.summary {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  border-bottom: none;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  color: #475569;
}

.summary-row.total {
  font-weight: 700;
  font-size: 14px;
  color: #1e293b;
}

.summary-value {
  color: #10b981;
  font-weight: 600;
}

.summary-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 8px 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eef2f6;
}

/* Тёмная тема */
body.dark-theme .exchange-page .page-title {
  color: #f1f5f9;
}

body.dark-theme .exchange-page .page-subtitle {
  color: #94a3b8;
}

body.dark-theme .exchange-page .tabs {
  border-color: #334155;
}

body.dark-theme .exchange-page .tab-btn {
  color: #94a3b8;
}

body.dark-theme .exchange-page .tab-btn:hover {
  color: #3b82f6;
}

body.dark-theme .exchange-page .tab-btn.active {
  color: #3b82f6;
}

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

body.dark-theme .offer-card {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .offer-value {
  color: #f1f5f9;
}

body.dark-theme .offer-label {
  color: #94a3b8;
}

body.dark-theme .offer-message {
  background: #1e3a5f;
  color: #3b82f6;
}

body.dark-theme .status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

body.dark-theme .status-badge.accepted {
  background: #ecfdf5;
  color: #059669;
}

body.dark-theme .status-badge.rejected,
body.dark-theme .status-badge.cancelled {
  background: #fef2f2;
  color: #dc2626;
}

body.dark-theme .offer-detail-section {
  border-color: #334155;
}

body.dark-theme .offer-detail-section h4 {
  color: #f1f5f9;
}

body.dark-theme .detail-value {
  color: #f1f5f9;
}

body.dark-theme .message-text {
  background: #0f172a;
}

body.dark-theme .coin-detail-item {
  background: #0f172a;
  border-color: #334155;
}

body.dark-theme .coin-detail-name {
  color: #f1f5f9;
}

body.dark-theme .offer-detail-section.summary {
  background: #0f172a;
}

body.dark-theme .summary-row {
  color: #cbd5e1;
}

body.dark-theme .summary-row.total {
  color: #f1f5f9;
}

body.dark-theme .modal-actions {
  border-color: #334155;
}

body.dark-theme .modal-container {
  background: #1e293b;
}

body.dark-theme .modal-header {
  border-color: #334155;
}

body.dark-theme .modal-header h3 {
  color: #f1f5f9;
}

body.dark-theme .modal-close {
  color: #94a3b8;
}

body.dark-theme .modal-close:hover {
  background: #334155;
}

@media (max-width: 640px) {
  .offer-coins {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .offer-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filters-grid {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 100%;
  }
  
  .modal-offer-detail {
    width: 95%;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: 100%;
    margin-bottom: 4px;
  }
  
  .coin-detail-item {
    flex-wrap: wrap;
  }
}
</style>