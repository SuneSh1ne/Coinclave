<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-header">
        <h1>{{ isEdit ? 'Редактирование монеты' : 'Новая монета' }}</h1>
        <p>{{ isEdit ? 'Измените параметры существующей монеты' : 'Заполните информацию о новой монете' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="form-card">
        <div class="form-grid">
          <div class="form-group">
            <label>Название монеты *</label>
            <input 
              type="text" 
              v-model="form.name" 
              placeholder="Например: 10 рублей 2000 г."
              required
            >
          </div>

          <div class="form-group">
            <label>Год чеканки *</label>
            <input 
              type="number" 
              v-model="form.year" 
              placeholder="2000"
              required
              min="0"
              :max="currentYear"
            >
          </div>

          <div class="form-group">
            <label>Страна *</label>
            <input 
              type="text" 
              v-model="form.country" 
              placeholder="Россия, США, Германия..."
              required
            >
          </div>

          <div class="form-group">
            <label>Номинал *</label>
            <input 
              type="text" 
              v-model="form.denomination" 
              placeholder="10 рублей, 1 доллар..."
              required
            >
          </div>

          <div class="form-group">
            <label>Металл *</label>
            <select v-model="form.metal" required>
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

          <div class="form-group">
            <label>Состояние *</label>
            <select v-model="form.condition" required>
              <option value="poor">Poor (Плохое)</option>
              <option value="fair">Fair (Удовлетворительное)</option>
              <option value="good">Good (Хорошее)</option>
              <option value="very_good">Very Good (Очень хорошее)</option>
              <option value="fine">Fine (Отличное)</option>
              <option value="very_fine">Very Fine (Очень отличное)</option>
              <option value="extremely_fine">Extremely Fine (Почти идеал)</option>
              <option value="uncirculated">Uncirculated (Идеал)</option>
            </select>
          </div>

          <div class="form-group">
            <label>Цена покупки (₽)</label>
            <input 
              type="number" 
              v-model="form.purchase_price" 
              placeholder="Сколько заплатили"
              step="0.01"
            >
          </div>

          <div class="form-group">
            <label>Оценочная стоимость (₽) *</label>
            <input 
              type="number" 
              v-model="form.estimated_value" 
              placeholder="Текущая рыночная стоимость"
              required
              step="0.01"
            >
          </div>
        </div>

        <div class="form-group">
          <label>Изображения</label>
          <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
            <input 
              type="file" 
              ref="fileInput"
              multiple 
              accept="image/jpeg,image/png,image/webp" 
              @change="handleFiles"
              style="display: none"
            >
            <button type="button" class="upload-btn" @click="$refs.fileInput.click()">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              Выбрать изображения
            </button>
            <p class="upload-hint">или перетащите файлы сюда</p>
            <p class="upload-limit">До 4 изображений (JPEG, PNG, WebP, до 5MB)</p>
          </div>
          
          <div v-if="previewImages.length || existingImages.length" class="preview-grid">
            <div v-for="(img, idx) in existingImages" :key="'existing-' + img.id" class="preview-item">
              <img :src="getImageUrl(img.image_path)" alt="Монета">
              <span class="preview-label">{{ img.is_obverse ? 'Аверс' : 'Реверс' }}</span>
              <button type="button" class="remove-btn" @click="removeExistingImage(img.id)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div v-for="(img, idx) in previewImages" :key="'new-' + idx" class="preview-item">
              <img :src="img.url" alt="Новое изображение">
              <span class="preview-label">{{ idx === 0 && existingImages.length === 0 ? 'Аверс' : 'Реверс' }}</span>
              <button type="button" class="remove-btn" @click="removePreview(idx)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$router.back()">Отмена</button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>{{ isEdit ? 'Сохранить изменения' : 'Добавить монету' }}</span>
          </button>
        </div>

        <div v-if="error" class="error-alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const currentYear = new Date().getFullYear()
const loading = ref(false)
const error = ref('')
const fileInput = ref(null)

const form = reactive({
  name: '',
  year: '',
  country: '',
  denomination: '',
  metal: 'silver',
  condition: 'very_good',
  purchase_price: null,
  estimated_value: ''
})

const images = ref([])
const previewImages = ref([])
const existingImages = ref([])
const imagesToDelete = ref([])

const getImageUrl = (path) => `http://localhost:8000/uploads/${path}`

const handleFiles = (e) => {
  const files = Array.from(e.target.files)
  addFiles(files)
}

const handleDrop = (e) => {
  const files = Array.from(e.dataTransfer.files)
  addFiles(files)
}

const addFiles = (files) => {
  const totalImages = images.value.length + existingImages.value.length + files.length
  
  if (totalImages > 4) {
    error.value = 'Максимум 4 изображения'
    return
  }
  
  files.forEach(file => {
    if (!file.type.match('image.*')) {
      error.value = 'Можно загружать только изображения'
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      error.value = 'Файл слишком большой (макс 5MB)'
      return
    }
    images.value.push(file)
    
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImages.value.push({ url: e.target.result, file: file })
    }
    reader.readAsDataURL(file)
  })
  error.value = ''
}

const removePreview = (idx) => {
  previewImages.value.splice(idx, 1)
  images.value.splice(idx, 1)
}

const removeExistingImage = async (imageId) => {
  try {
    await api.delete(`/api/coins/images/${imageId}`)
    existingImages.value = existingImages.value.filter(img => img.id !== imageId)
  } catch (e) {
    error.value = 'Ошибка при удалении изображения'
  }
}

const loadCoin = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await api.get(`/api/coins/${route.params.id}`)
    const coin = res.data
    
    form.name = coin.name
    form.year = coin.year
    form.country = coin.country
    form.denomination = coin.denomination
    form.metal = coin.metal
    form.condition = coin.condition
    form.purchase_price = coin.purchase_price
    form.estimated_value = coin.estimated_value
    
    existingImages.value = coin.images || []
  } catch (e) {
    error.value = 'Ошибка загрузки монеты'
  }
}

const handleSubmit = async () => {
  if (!form.name || !form.year || !form.country || !form.denomination || !form.estimated_value) {
    error.value = 'Заполните все обязательные поля'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('year', form.year)
    formData.append('country', form.country)
    formData.append('denomination', form.denomination)
    formData.append('metal', form.metal)
    formData.append('condition', form.condition)
    if (form.purchase_price) formData.append('purchase_price', form.purchase_price)
    formData.append('estimated_value', form.estimated_value)
    
    images.value.forEach(img => {
      formData.append('images', img)
    })
    
    if (isEdit.value) {
      await api.put(`/api/coins/${route.params.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post('/api/coins', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCoin()
})
</script>

<style scoped>
.form-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px;
}

.form-container {
  background: white;
  border-radius: 24px;
  border: 1px solid #eef2f6;
  overflow: hidden;
}

.form-header {
  padding: 24px 28px;
  border-bottom: 1px solid #eef2f6;
}

.form-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.form-header p {
  font-size: 13px;
  color: #94a3b8;
}

.form-card {
  padding: 28px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.upload-area {
  border: 2px dashed #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-btn {
  background: none;
  border: none;
  color: #3b82f6;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #94a3b8;
}

.upload-limit {
  font-size: 11px;
  color: #cbd5e1;
  margin-top: 8px;
}

.preview-grid {
  display: flex;
  gap: 16px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-label {
  position: absolute;
  bottom: 4px;
  left: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
}

.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: #ef4444;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #eef2f6;
}

.btn-secondary, .btn-primary {
  padding: 10px 28px;
  border-radius: 12px;
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

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.6s linear infinite;
}

.error-alert {
  margin-top: 20px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 12px;
  color: #ef4444;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-card {
    padding: 20px;
  }
}
</style>