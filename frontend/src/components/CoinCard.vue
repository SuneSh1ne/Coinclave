<template>
  <div class="coin-card" @click="$emit('click')">
    <div class="coin-image">
      <img v-if="coin.images && coin.images[0]" :src="getImageUrl(coin.images[0].image_path)" :alt="coin.name">
      <div v-else class="image-placeholder">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
      </div>
      <div v-if="isOnExchange" class="exchange-badge">Exchange</div>
      <div class="card-actions">
        <router-link :to="`/coin/${coin.id}`" class="action-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </router-link>
        <router-link :to="`/coin/${coin.id}/edit`" class="action-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 3l4 4-7 7H10v-4l7-7z"/>
            <path d="M4 20h16"/>
          </svg>
        </router-link>
        <button class="action-btn delete" @click.stop="$emit('delete')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 7h16M10 11v6M14 11v6M5 7l1 13a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-13M9 3h6v4H9z"/>
          </svg>
        </button>
      </div>
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
    very_good: 'VG',
    fine: 'Fine',
    very_fine: 'VF',
    extremely_fine: 'XF',
    uncirculated: 'UNC'
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
  height: 220px;
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

.card-actions {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.coin-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #64748b;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.action-btn:hover {
  background: #f1f5f9;
  color: #3b82f6;
}

.action-btn.delete:hover {
  background: #fef2f2;
  color: #ef4444;
  border-color: #fee2e2;
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
</style>