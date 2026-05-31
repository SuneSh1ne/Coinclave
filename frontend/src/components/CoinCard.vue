<template>
  <div class="coin-card" @click="$emit('click')">
    <div class="coin-image">
      <img v-if="coin.images && coin.images[0]" :src="getImageUrl(coin.images[0].image_path)" :alt="coin.name">
      <div v-else class="image-placeholder">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="2" width="20" height="20" rx="2.18"/>
          <circle cx="8.5" cy="8.5" r="2.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
      </div>
      <div v-if="isOnExchange" class="exchange-badge">Exchange</div>
    </div>
    
    <div class="coin-info">
      <h3 class="coin-title">{{ coin.name }}</h3>
      <div class="coin-meta">
        <span>{{ coin.year }}</span>
        <span class="separator">•</span>
        <span>{{ coin.country }}</span>
      </div>
      <div class="coin-tags">
        <span class="tag metal">{{ getMetalName(coin.metal) }}</span>
        <span class="tag condition" :class="getConditionClass(coin.condition)">{{ getConditionName(coin.condition) }}</span>
      </div>
      <div class="coin-value">
        <span class="value">{{ formatPrice(coin.estimated_value) }} ₽</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  coin: Object,
  isOnExchange: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click', 'delete'])

const getImageUrl = (path) => `http://localhost:8000/uploads/${path}`

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price))
}

const getMetalName = (metal) => {
  const metals = {
    gold: 'Золото',
    silver: 'Серебро',
    copper: 'Медь',
    nickel: 'Никель',
    brass: 'Латунь',
    bronze: 'Бронза',
    aluminum: 'Алюминий',
    bimetallic: 'Биметалл'
  }
  return metals[metal] || metal
}

const getConditionName = (condition) => {
  const conditions = {
    poor: 'Poor',
    fair: 'Fair',
    good: 'Good',
    very_good: 'Very Good',
    fine: 'Fine',
    very_fine: 'Very Fine',
    extremely_fine: 'Extremely Fine',
    uncirculated: 'Uncirculated'
  }
  return conditions[condition] || condition
}

const getConditionClass = (condition) => {
  const classes = {
    poor: 'condition-poor',
    fair: 'condition-fair',
    good: 'condition-good',
    very_good: 'condition-vg',
    fine: 'condition-fine',
    very_fine: 'condition-vf',
    extremely_fine: 'condition-xf',
    uncirculated: 'condition-unc'
  }
  return classes[condition] || ''
}
</script>

<style scoped>
.coin-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid #eef2f6;
}

.coin-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.coin-image {
  position: relative;
  height: 200px;
  background: #f8fafc;
  overflow: hidden;
}

.coin-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.coin-card:hover .coin-image img {
  transform: scale(1.05);
}

.image-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.image-placeholder svg {
  stroke: #cbd5e1;
}

.exchange-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #10b981;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.coin-info {
  padding: 16px;
}

.coin-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  gap: 8px;
  margin-bottom: 14px;
}

.tag {
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.metal {
  background: #f1f5f9;
  color: #475569;
}

.condition-poor { background: #fef2f2; color: #ef4444; }
.condition-fair { background: #fffbeb; color: #f59e0b; }
.condition-good { background: #eff6ff; color: #3b82f6; }
.condition-vg { background: #e0f2fe; color: #0ea5e9; }
.condition-fine { background: #ecfdf5; color: #10b981; }
.condition-vf { background: #ecfdf5; color: #10b981; }
.condition-xf { background: #fef3c7; color: #d97706; }
.condition-unc { background: #fef3c7; color: #d97706; }

.coin-value {
  border-top: 1px solid #f0f2f5;
  padding-top: 12px;
}

.value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

/* Тёмная тема */
body.dark-theme .coin-card {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .coin-title {
  color: #f1f5f9;
}

body.dark-theme .coin-meta {
  color: #94a3b8;
}

body.dark-theme .metal {
  background: #334155;
  color: #94a3b8;
}

body.dark-theme .value {
  color: #10b981;
}

body.dark-theme .coin-value {
  border-color: #334155;
}

body.dark-theme .coin-image {
  background: #0f172a;
}

body.dark-theme .image-placeholder {
  background: #0f172a;
}

body.dark-theme .image-placeholder svg {
  stroke: #475569;
}
</style>