<template>
  <div class="home-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Главная</h1>
        <p class="page-subtitle">Новые поступления из коллекций пользователей</p>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-header">
        <h3 class="filter-title">Фильтрация монет</h3>
        <button @click="resetFilters" class="reset-btn">Сбросить все</button>
      </div>
      
      <div class="filters-grid">
        <div class="filter-group">
          <input 
            type="text" 
            v-model="filters.search" 
            placeholder="Поиск по названию..."
            @input="debouncedFetchFeed"
            class="filter-input"
          >
        </div>
        
        <div class="filter-group">
          <select v-model="filters.country" @change="fetchFeed" class="filter-select">
            <option value="">Все страны</option>
            <option v-for="c in availableCountries" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        
        <div class="filter-group">
          <select v-model="filters.metal" @change="fetchFeed" class="filter-select">
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
            v-model="filters.year_from" 
            placeholder="Год от"
            @input="fetchFeed"
            class="filter-input"
          >
        </div>
        
        <div class="filter-group">
          <input 
            type="number" 
            v-model="filters.year_to" 
            placeholder="Год до"
            @input="fetchFeed"
            class="filter-input"
          >
        </div>
        
        <div class="filter-group">
          <select v-model="filters.condition" @change="fetchFeed" class="filter-select">
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

    <div class="feed-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка монет...</p>
      </div>

      <div v-else-if="feed.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="none" stroke="#94a3b8" stroke-width="2"/>
          <rect x="10.5" y="6" width="3" height="9" rx="1.5" fill="#94a3b8"/>
          <circle cx="12" cy="18" r="1.5" fill="#94a3b8"/>
        </svg>
        <h3>Нет монет в каталоге</h3>
        <p>Будьте первым, кто добавит монету!</p>
      </div>

      <div v-else class="feed-grid">
        <div v-for="(item, index) in feed" :key="item.id" class="feed-card" :style="{ animationDelay: (index * 0.05) + 's' }">
          <div class="card-image" @click="openDetailModal(item)">
            <img v-if="item.images && item.images[0]" :src="getImageUrl(item.images[0].image_path)" :alt="item.name">
            <div v-else class="image-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                <circle cx="8.5" cy="8.5" r="2.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
          </div>
          <div class="card-info">
            <h3 class="card-title" @click="openDetailModal(item)">{{ item.name }}</h3>
            <div class="card-meta" @click="openDetailModal(item)">
              <span>{{ item.year }} г.</span>
              <span class="separator">•</span>
              <span>{{ item.country }}</span>
            </div>
            <div class="card-tags" @click="openDetailModal(item)">
              <span class="tag">{{ getMetalName(item.metal) }}</span>
              <span class="tag condition">{{ getConditionName(item.condition) }}</span>
            </div>
            <div class="card-footer">
              <div class="owner-info">
                <span class="owner-label">Владелец:</span>
                <span class="owner-name" @click.stop="goToUser(item.owner_id)">
                  {{ item.owner_name }}
                </span>
              </div>
              <div class="card-actions">
                <span class="value" @click="openDetailModal(item)">{{ formatPrice(item.estimated_value) }} ₽</span>
                <button 
                  v-if="isAuthenticated && item.owner_id !== currentUserId" 
                  class="offer-btn"
                  @click.stop="openMultiExchangeModal(item)"
                >
                  Предложить обмен
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно деталей монеты -->
    <div v-if="detailModalCoin" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3>{{ detailModalCoin.name }}</h3>
          <button class="modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body modal-body-detail">
          <div class="modal-gallery">
            <div class="modal-main-image">
              <img v-if="detailCurrentImage" :src="getImageUrl(detailCurrentImage.image_path)" :alt="detailModalCoin.name">
              <div v-else class="no-image-modal">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                  <circle cx="8.5" cy="8.5" r="2.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
            </div>
            <div class="modal-thumbnails" v-if="detailModalCoin.images && detailModalCoin.images.length > 1">
              <div 
                v-for="img in detailModalCoin.images" 
                :key="img.id" 
                class="modal-thumb"
                :class="{ active: detailCurrentImage?.id === img.id }"
                @click="detailCurrentImage = img"
              >
                <img :src="getImageUrl(img.image_path)" :alt="img.is_obverse ? 'Аверс' : 'Реверс'">
              </div>
            </div>
          </div>
          <div class="modal-info">
            <div class="info-row">
              <span class="info-label">Год чеканки</span>
              <span class="info-value">{{ detailModalCoin.year }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Страна</span>
              <span class="info-value">{{ detailModalCoin.country }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Номинал</span>
              <span class="info-value">{{ detailModalCoin.denomination }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Металл</span>
              <span class="info-value">{{ getMetalName(detailModalCoin.metal) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Состояние</span>
              <span class="info-value">
                <span class="condition-badge" :class="getConditionClass(detailModalCoin.condition)">
                  {{ getConditionName(detailModalCoin.condition) }}
                </span>
              </span>
            </div>
            <div class="info-row highlight">
              <span class="info-label">Оценочная стоимость</span>
              <span class="info-value">{{ formatPrice(detailModalCoin.estimated_value) }} ₽</span>
            </div>
            <div class="info-row">
              <span class="info-label">Владелец</span>
              <span class="info-value owner-link" @click="goToUser(detailModalCoin.owner_id)">
                {{ detailModalCoin.owner_name }}
              </span>
            </div>
            <div class="modal-actions-detail">
              <button 
                v-if="isAuthenticated && detailModalCoin.owner_id !== currentUserId" 
                class="btn-offer-full"
                @click="openMultiExchangeFromDetail"
              >
                Предложить обмен
              </button>
              <button 
                v-if="!isAuthenticated" 
                class="btn-offer-full"
                @click="router.push('/login')"
              >
                Войдите, чтобы предложить обмен
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно множественного обмена -->
    <div v-if="showMultiModal" class="modal-overlay" @click.self="closeMultiModal">
      <div class="modal-container modal-multi-exchange">
        <div class="modal-header">
          <h3>Предложение обмена</h3>
          <button class="modal-close" @click="closeMultiModal">×</button>
        </div>
        <div class="modal-body multi-exchange-body">
          <!-- Левая колонка - мои монеты (что отдаю) -->
          <div class="exchange-column">
            <div class="column-header">
              <h4>Я отдаю</h4>
              <button class="select-all-btn" @click="toggleSelectAllMyCoins">
                {{ allMyCoinsSelected ? 'Снять все' : 'Выбрать все' }}
              </button>
            </div>
            <div class="column-subheader">
              <span>Можно выбрать несколько монет</span>
            </div>
            <div class="coins-list">
              <div 
                v-for="coin in myCoins" 
                :key="coin.id" 
                class="coin-select-item"
                :class="{ selected: selectedMyCoinIds.includes(coin.id) }"
                @click="toggleMyCoin(coin.id)"
              >
                <div class="coin-select-image">
                  <img v-if="coin.images && coin.images[0]" :src="getImageUrl(coin.images[0].image_path)" :alt="coin.name">
                  <div v-else class="small-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                      <circle cx="8.5" cy="8.5" r="2.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                  </div>
                </div>
                <div class="coin-select-info">
                  <div class="coin-select-name">{{ coin.name }}</div>
                  <div class="coin-select-meta">{{ coin.year }} г., {{ coin.country }}</div>
                  <div class="coin-select-value">{{ formatPrice(coin.estimated_value) }} ₽</div>
                </div>
                <div class="coin-select-checkbox">
                  <svg v-if="selectedMyCoinIds.includes(coin.id)" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <div v-else class="empty-checkbox"></div>
                </div>
              </div>
              <div v-if="myCoins.length === 0" class="empty-coins-list">
                <p>У вас нет монет</p>
                <router-link to="/add" class="small-link">Добавить монету</router-link>
              </div>
            </div>
            <div class="column-summary" v-if="selectedMyCoinIds.length > 0">
              <span>Выбрано: {{ selectedMyCoinIds.length }} монет</span>
              <span class="summary-value">{{ formatPrice(selectedMyTotalValue) }} ₽</span>
            </div>
          </div>

          <!-- Правая колонка - монеты пользователя (что получаю) -->
          <div class="exchange-column">
            <div class="column-header">
              <h4>Я получаю</h4>
              <button class="select-all-btn" @click="toggleSelectAllTargetCoins">
                {{ allTargetCoinsSelected ? 'Снять все' : 'Выбрать все' }}
              </button>
            </div>
            <div class="column-subheader">
              <span>Можно выбрать несколько монет</span>
            </div>
            <div class="coins-list">
              <div 
                v-for="coin in targetUserCoins" 
                :key="coin.id" 
                class="coin-select-item"
                :class="{ selected: selectedTargetCoinIds.includes(coin.id), preselected: coin.id === preselectedCoinId }"
                @click="toggleTargetCoin(coin.id)"
              >
                <div class="coin-select-image">
                  <img v-if="coin.images && coin.images[0]" :src="getImageUrl(coin.images[0].image_path)" :alt="coin.name">
                  <div v-else class="small-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                      <circle cx="8.5" cy="8.5" r="2.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                  </div>
                </div>
                <div class="coin-select-info">
                  <div class="coin-select-name">{{ coin.name }}</div>
                  <div class="coin-select-meta">{{ coin.year }} г., {{ coin.country }}</div>
                  <div class="coin-select-value">{{ formatPrice(coin.estimated_value) }} ₽</div>
                </div>
                <div class="coin-select-checkbox">
                  <svg v-if="selectedTargetCoinIds.includes(coin.id)" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <div v-else class="empty-checkbox"></div>
                </div>
              </div>
              <div v-if="targetUserCoins.length === 0" class="empty-coins-list">
                <p>У пользователя нет монет</p>
              </div>
            </div>
            <div class="column-summary" v-if="selectedTargetCoinIds.length > 0">
              <span>Выбрано: {{ selectedTargetCoinIds.length }} монет</span>
              <span class="summary-value">{{ formatPrice(selectedTargetTotalValue) }} ₽</span>
            </div>
          </div>
        </div>
        <div class="exchange-summary" v-if="selectedMyCoinIds.length > 0 || selectedTargetCoinIds.length > 0">
          <div class="summary-row" v-if="selectedMyCoinIds.length > 0">
            <span>Я отдаю:</span>
            <span class="summary-value">{{ selectedMyCoinIds.length }} монет ({{ formatPrice(selectedMyTotalValue) }} ₽)</span>
          </div>
          <div class="summary-row" v-if="selectedTargetCoinIds.length > 0">
            <span>Я получаю:</span>
            <span class="summary-value">{{ selectedTargetCoinIds.length }} монет ({{ formatPrice(selectedTargetTotalValue) }} ₽)</span>
          </div>
          <div class="summary-divider" v-if="selectedMyCoinIds.length > 0 && selectedTargetCoinIds.length > 0"></div>
          <div class="summary-row total" v-if="selectedMyCoinIds.length > 0 && selectedTargetCoinIds.length > 0">
            <span>Итого:</span>
            <span class="summary-value">{{ formatPrice(Math.abs(selectedMyTotalValue - selectedTargetTotalValue)) }} ₽ разница</span>
          </div>
          <div class="summary-row" v-if="selectedMyCoinIds.length > 0 && selectedTargetCoinIds.length === 0">
            <span>Вы дарите {{ selectedMyCoinIds.length }} монет</span>
          </div>
          <div class="summary-row" v-if="selectedMyCoinIds.length === 0 && selectedTargetCoinIds.length > 0">
            <span>Вы запрашиваете {{ selectedTargetCoinIds.length }} монет</span>
          </div>
        </div>
        <div class="modal-footer">
          <div class="form-group message-group">
            <label>Сообщение (необязательно)</label>
            <textarea v-model="multiOfferMessage" class="form-textarea" rows="2" placeholder="Добавьте комментарий к предложению..."></textarea>
          </div>
          <div class="footer-buttons">
            <button class="btn-secondary" @click="closeMultiModal">Отмена</button>
            <button 
            class="btn-primary" 
            @click="sendMultiOffer" 
            :disabled="selectedMyCoinIds.length === 0 && selectedTargetCoinIds.length === 0"
          >
            Отправить предложение
          </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const feed = ref([])
const loading = ref(false)
const availableCountries = ref([])
const myCoins = ref([])
const targetUserCoins = ref([])
const currentUserId = ref(null)
const targetUserId = ref(null)

const showMultiModal = ref(false)
const preselectedCoinId = ref(null)
const selectedMyCoinIds = ref([])
const selectedTargetCoinIds = ref([])
const multiOfferMessage = ref('')

const detailModalCoin = ref(null)
const detailCurrentImage = ref(null)

const isAuthenticated = computed(() => !!localStorage.getItem('token'))

const selectedMyTotalValue = computed(() => {
  return myCoins.value
    .filter(c => selectedMyCoinIds.value.includes(c.id))
    .reduce((sum, c) => sum + (c.estimated_value || 0), 0)
})

const selectedTargetTotalValue = computed(() => {
  return targetUserCoins.value
    .filter(c => selectedTargetCoinIds.value.includes(c.id))
    .reduce((sum, c) => sum + (c.estimated_value || 0), 0)
})

const allMyCoinsSelected = computed(() => {
  return myCoins.value.length > 0 && selectedMyCoinIds.value.length === myCoins.value.length
})

const allTargetCoinsSelected = computed(() => {
  return targetUserCoins.value.length > 0 && selectedTargetCoinIds.value.length === targetUserCoins.value.length
})

const filters = ref({
  search: '',
  country: '',
  metal: '',
  year_from: '',
  year_to: '',
  condition: ''
})

let debounceTimer = null
const debouncedFetchFeed = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchFeed()
  }, 300)
}

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

const fetchFeed = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.country) params.country = filters.value.country
    if (filters.value.metal) params.metal = filters.value.metal
    if (filters.value.year_from) params.year_from = filters.value.year_from
    if (filters.value.year_to) params.year_to = filters.value.year_to
    if (filters.value.condition) params.condition = filters.value.condition
    if (filters.value.search) params.search = filters.value.search
    
    const res = await api.get('/public/feed', { params })
    feed.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const fetchCountries = async () => {
  try {
    const res = await api.get('/public/filters/countries')
    availableCountries.value = res.data.countries
  } catch (e) {
    console.error(e)
  }
}

const fetchMyCoins = async () => {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/api/coins')
    myCoins.value = res.data.items
  } catch (e) {}
}

const fetchTargetUserCoins = async (userId) => {
  try {
    const res = await api.get(`/users/${userId}/collection`)
    targetUserCoins.value = res.data.coins
  } catch (e) {}
}

const fetchCurrentUser = async () => {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/auth/me')
    currentUserId.value = res.data.id
  } catch (e) {}
}

const resetFilters = () => {
  filters.value = {
    search: '',
    country: '',
    metal: '',
    year_from: '',
    year_to: '',
    condition: ''
  }
  fetchFeed()
}

const goToUser = (userId) => {
  closeDetailModal()
  if (isAuthenticated.value) {
    router.push(`/user/${userId}`)
  } else {
    router.push('/login')
  }
}

const openDetailModal = (coin) => {
  detailModalCoin.value = coin
  detailCurrentImage.value = coin.images?.[0] || null
  document.body.classList.add('modal-open')
}

const closeDetailModal = () => {
  detailModalCoin.value = null
  document.body.classList.remove('modal-open')
}

const openMultiExchangeModal = async (coin) => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }
  
  closeDetailModal()
  
  preselectedCoinId.value = coin.id
  targetUserId.value = coin.owner_id
  selectedMyCoinIds.value = []
  selectedTargetCoinIds.value = [coin.id]
  multiOfferMessage.value = ''
  
  await Promise.all([
    fetchMyCoins(),
    fetchTargetUserCoins(coin.owner_id)
  ])
  
  showMultiModal.value = true
  document.body.classList.add('modal-open')
}

const openMultiExchangeFromDetail = () => {
  openMultiExchangeModal(detailModalCoin.value)
}

const closeMultiModal = () => {
  showMultiModal.value = false
  selectedMyCoinIds.value = []
  selectedTargetCoinIds.value = []
  preselectedCoinId.value = null
  targetUserId.value = null
  document.body.classList.remove('modal-open')
}

const toggleMyCoin = (coinId) => {
  const index = selectedMyCoinIds.value.indexOf(coinId)
  if (index === -1) {
    selectedMyCoinIds.value.push(coinId)
  } else {
    selectedMyCoinIds.value.splice(index, 1)
  }
}

const toggleTargetCoin = (coinId) => {
  const index = selectedTargetCoinIds.value.indexOf(coinId)
  if (index === -1) {
    selectedTargetCoinIds.value.push(coinId)
  } else {
    selectedTargetCoinIds.value.splice(index, 1)
  }
}

const toggleSelectAllMyCoins = () => {
  if (allMyCoinsSelected.value) {
    selectedMyCoinIds.value = []
  } else {
    selectedMyCoinIds.value = myCoins.value.map(c => c.id)
  }
}

const toggleSelectAllTargetCoins = () => {
  if (allTargetCoinsSelected.value) {
    selectedTargetCoinIds.value = []
  } else {
    selectedTargetCoinIds.value = targetUserCoins.value.map(c => c.id)
  }
}

const sendMultiOffer = async () => {
  // Проверяем, что выбраны монеты хотя бы в одной колонке
  if (selectedMyCoinIds.value.length === 0 && selectedTargetCoinIds.value.length === 0) {
    return
  }
  
  try {
    // Подарок: только свои монеты
    if (selectedMyCoinIds.value.length > 0 && selectedTargetCoinIds.value.length === 0) {
      // Получаем владельца из preselectedCoinId
      const targetCoin = feed.value.find(c => c.id === preselectedCoinId.value)
      if (!targetCoin) {
        return
      }
      
      await api.post('/exchange/offers/batch', {
        offered_coin_ids: selectedMyCoinIds.value,
        requested_coin_ids: null,
        to_user_id: targetCoin.owner_id,
        message: multiOfferMessage.value
      })
    }
    // Запрос: только чужие монеты
    else if (selectedMyCoinIds.value.length === 0 && selectedTargetCoinIds.value.length > 0) {
      await api.post('/exchange/offers/batch', {
        offered_coin_ids: null,
        requested_coin_ids: selectedTargetCoinIds.value,
        to_user_id: null,
        message: multiOfferMessage.value
      })
    }
    // Обмен: и свои, и чужие
    else {
      await api.post('/exchange/offers/batch', {
        offered_coin_ids: selectedMyCoinIds.value,
        requested_coin_ids: selectedTargetCoinIds.value,
        to_user_id: null,
        message: multiOfferMessage.value
      })
    }
    
    closeMultiModal()
  } catch (e) {
  }
}

onMounted(() => {
  fetchFeed()
  fetchCountries()
  fetchCurrentUser()
})
</script>

<style scoped>
.home-page {
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

.feed-section {
  margin-top: 0;
}

.feed-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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

.feed-card {
  background: white;
  border-radius: 20px;
  border: 1px solid #eef2f6;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  opacity: 0;
  animation: fadeInUp 0.4s ease-out forwards;
}

.feed-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.card-image {
  height: 200px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.feed-card:hover .card-image img {
  transform: scale(1.05);
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  width: 100%;
  height: 100%;
}

.image-placeholder svg {
  stroke: #cbd5e1;
}

.card-info {
  padding: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
  cursor: pointer;
}

.card-title:hover {
  color: #3b82f6;
}

.card-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 10px;
  cursor: pointer;
}

.separator {
  margin: 0 6px;
}

.card-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
  flex-wrap: wrap;
  cursor: pointer;
}

.tag {
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
}

.tag.condition {
  background: #eff6ff;
  color: #3b82f6;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
  flex-wrap: wrap;
  gap: 10px;
}

.owner-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.owner-label {
  color: #94a3b8;
}

.owner-name {
  color: #3b82f6;
  cursor: pointer;
  font-weight: 500;
}

.owner-name:hover {
  text-decoration: underline;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.value {
  font-weight: 700;
  color: #1e293b;
  cursor: pointer;
}

.offer-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.offer-btn:hover {
  background: #059669;
  transform: translateY(-1px);
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

.empty-state svg {
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

.empty-state p {
  color: #94a3b8;
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

.modal-large {
  width: 900px;
}

.modal-multi-exchange {
  width: 1100px;
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

.modal-body-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 24px;
}

.multi-exchange-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 24px;
  max-height: 500px;
  overflow-y: auto;
}

.exchange-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.column-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.select-all-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #3b82f6;
  cursor: pointer;
}

.column-subheader {
  font-size: 11px;
  color: #94a3b8;
  padding-bottom: 8px;
  border-bottom: 1px solid #eef2f6;
}

.coins-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 350px;
  overflow-y: auto;
}

.coin-select-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.coin-select-item:hover {
  background: #f8fafc;
  border-color: #3b82f6;
}

.coin-select-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.coin-select-item.preselected {
  background: #fef3c7;
  border-color: #f59e0b;
}

.coin-select-image {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coin-select-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.small-placeholder {
  font-size: 24px;
}

.coin-select-info {
  flex: 1;
}

.coin-select-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.coin-select-meta {
  font-size: 11px;
  color: #94a3b8;
}

.coin-select-value {
  font-size: 12px;
  font-weight: 600;
  color: #10b981;
}

.coin-select-checkbox {
  width: 24px;
  display: flex;
  justify-content: center;
}

.empty-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-radius: 4px;
}

.empty-coins-list {
  text-align: center;
  padding: 30px;
  color: #94a3b8;
  font-size: 13px;
}

.small-link {
  font-size: 12px;
  color: #3b82f6;
  text-decoration: none;
}

.column-summary {
  padding: 10px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.summary-value {
  color: #10b981;
  font-weight: 600;
}

.exchange-summary {
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #eef2f6;
  border-bottom: 1px solid #eef2f6;
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

.summary-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 8px 0;
}

.modal-footer {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-group {
  margin-bottom: 0;
}

.message-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13px;
  resize: vertical;
  background: white;
}

.footer-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary {
  background: #f1f5f9;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 13px;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 13px;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.no-image-modal {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  width: 100%;
  height: 100%;
}

.no-image-modal svg {
  stroke: #cbd5e1;
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

.owner-link {
  color: #3b82f6;
  cursor: pointer;
  text-decoration: none;
}

.owner-link:hover {
  text-decoration: underline;
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

.modal-actions-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eef2f6;
}

.btn-offer-full {
  width: 100%;
  background: #10b981;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-offer-full:hover {
  background: #059669;
  transform: translateY(-1px);
}

/* Тёмная тема */
body.dark-theme .home-page {
  background: #0f172a;
}

body.dark-theme .page-title {
  color: #f1f5f9;
}

body.dark-theme .page-subtitle {
  color: #94a3b8;
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

body.dark-theme .feed-card {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .card-title {
  color: #f1f5f9;
}

body.dark-theme .card-meta {
  color: #94a3b8;
}

body.dark-theme .tag {
  background: #334155;
  color: #94a3b8;
}

body.dark-theme .tag.condition {
  background: #1e3a5f;
  color: #3b82f6;
}

body.dark-theme .card-footer {
  border-color: #334155;
}

body.dark-theme .value {
  color: #10b981;
}

body.dark-theme .card-image {
  background: #0f172a;
}

body.dark-theme .image-placeholder {
  background: #0f172a;
}

body.dark-theme .image-placeholder svg {
  stroke: #475569;
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

body.dark-theme .modal-main-image {
  background: #0f172a;
}

body.dark-theme .no-image-modal {
  background: #0f172a;
}

body.dark-theme .no-image-modal svg {
  stroke: #475569;
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

body.dark-theme .condition-badge {
  background: #1e3a5f;
  color: #3b82f6;
}

/* Тёмная тема для множественного обмена */
body.dark-theme .column-header h4 {
  color: #f1f5f9;
}

body.dark-theme .column-subheader {
  color: #94a3b8;
  border-color: #334155;
}

body.dark-theme .column-summary {
  background: #0f172a;
  border-color: #334155;
  color: #cbd5e1;
}

body.dark-theme .column-summary .summary-value {
  color: #10b981;
}

body.dark-theme .empty-coins-list {
  color: #64748b;
}

body.dark-theme .small-placeholder {
  color: #94a3b8;
}

body.dark-theme .coin-select-checkbox .empty-checkbox {
  border-color: #475569;
}

body.dark-theme .exchange-summary {
  background: #0f172a;
  border-color: #334155;
}

body.dark-theme .exchange-summary .summary-row {
  color: #cbd5e1;
}

body.dark-theme .exchange-summary .summary-row.total {
  color: #f1f5f9;
}

body.dark-theme .exchange-summary .summary-value {
  color: #10b981;
}

body.dark-theme .exchange-summary .summary-divider {
  background: #334155;
}

body.dark-theme .coin-select-item {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .coin-select-item:hover {
  background: #334155;
}

body.dark-theme .coin-select-item.selected {
  background: #1e3a5f;
}

body.dark-theme .coin-select-name {
  color: #f1f5f9;
}

body.dark-theme .coin-select-meta {
  color: #94a3b8;
}

body.dark-theme .form-textarea {
  background: #0f172a;
  border-color: #334155;
  color: #f1f5f9;
}

body.dark-theme .btn-secondary {
  background: #334155;
  color: #f1f5f9;
}

body.dark-theme .message-group label {
  color: #cbd5e1;
}

@media (max-width: 768px) {
  .multi-exchange-body {
    grid-template-columns: 1fr;
  }
  
  .modal-multi-exchange {
    width: 95%;
  }
  
  .filters-grid {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 100%;
  }
}
</style>