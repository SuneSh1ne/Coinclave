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
          
          <!-- Область загрузки с превью внутри -->
          <div 
            class="upload-area" 
            :class="{ 'has-images': allImagesPreview.length > 0 }"
            @dragover.prevent 
            @drop.prevent="handleDrop"
          >
            <input 
              type="file" 
              ref="fileInput"
              multiple 
              accept="image/jpeg,image/png,image/webp" 
              @change="handleFiles"
              style="display: none"
            >
            
            <!-- Превью изображений внутри области -->
            <div v-if="allImagesPreview.length > 0" class="upload-preview-grid">
              <div v-for="(img, idx) in allImagesPreview" :key="idx" class="upload-preview-item">
                <img :src="img.url" :alt="'Изображение ' + (idx + 1)">
                <button type="button" class="upload-remove-btn" @click.stop="removeImage(idx)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
                <span class="upload-preview-label">{{ getImageLabelByIndex(idx) }}</span>
              </div>
              
              <!-- Кнопка добавления ещё фото (если меньше 4) -->
              <div v-if="allImagesPreview.length < 4" class="upload-add-more" @click="$refs.fileInput.click()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12h14"/>
                </svg>
                <span>Добавить</span>
              </div>
            </div>
            
            <!-- Пустое состояние области -->
            <div v-else class="upload-empty" @click="$refs.fileInput.click()">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="2" width="20" height="20" rx="2.18"/>
                <circle cx="8.5" cy="8.5" r="2.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <p>Нажмите или перетащите изображения</p>
              <span>JPEG, PNG, WebP, до 5MB</span>
            </div>
          </div>
          
          <p class="upload-hint">Максимум 4 изображения. Первое будет аверсом, второе - реверсом.</p>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$router.back()">Отмена</button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>{{ isEdit ? 'Сохранить изменения' : 'Добавить монету' }}</span>
          </button>
        </div>

        <div v-if="error" class="error-alert">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="none" stroke="#ef4444" stroke-width="2"/>
            <rect x="10.5" y="6" width="3" height="9" rx="1.5" fill="#ef4444"/>
            <circle cx="12" cy="18" r="1.5" fill="#ef4444"/>
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

// Новые файлы
const newImages = ref([])
// Превью всех изображений (существующие + новые)
const allImagesPreview = ref([])
// Существующие изображения из БД
const existingImages = ref([])

const getImageUrl = (path) => `http://localhost:8000/uploads/${path}`

const getImageLabelByIndex = (idx) => {
  if (idx === 0) return 'Аверс'
  if (idx === 1) return 'Реверс'
  return `Фото ${idx + 1}`
}

// Обновить общее превью
const updateAllPreview = () => {
  const previews = []
  
  // Добавляем существующие изображения
  for (const img of existingImages.value) {
    previews.push({
      url: getImageUrl(img.image_path),
      isExisting: true,
      id: img.id,
      is_obverse: img.is_obverse
    })
  }
  
  // Добавляем новые изображения
  for (const img of newImages.value) {
    previews.push({
      url: URL.createObjectURL(img.file),
      isExisting: false,
      file: img.file
    })
  }
  
  allImagesPreview.value = previews
}

const handleFiles = (e) => {
  const files = Array.from(e.target.files)
  addFiles(files)
  if (fileInput.value) fileInput.value.value = ''
}

const handleDrop = (e) => {
  const files = Array.from(e.dataTransfer.files)
  addFiles(files)
}

const addFiles = (files) => {
  const totalImages = existingImages.value.length + newImages.value.length + files.length
  
  if (totalImages > 4) {
    error.value = 'Максимум 4 изображения'
    return
  }
  
  for (const file of files) {
    if (!file.type.match('image.*')) {
      error.value = 'Можно загружать только изображения'
      continue
    }
    if (file.size > 5 * 1024 * 1024) {
      error.value = 'Файл слишком большой (макс 5MB)'
      continue
    }
    
    newImages.value.push({ file })
  }
  
  updateAllPreview()
  error.value = ''
}

const removeImage = (idx) => {
  const imageToRemove = allImagesPreview.value[idx]
  
  if (imageToRemove.isExisting) {
    // Удаляем существующее изображение
    const existingIdx = existingImages.value.findIndex(img => img.id === imageToRemove.id)
    if (existingIdx !== -1) {
      existingImages.value.splice(existingIdx, 1)
    }
  } else {
    // Удаляем новое изображение
    const newIdx = newImages.value.findIndex(img => img.file === imageToRemove.file)
    if (newIdx !== -1) {
      newImages.value.splice(newIdx, 1)
    }
  }
  
  updateAllPreview()
}

const removeExistingImageFromServer = async (imageId) => {
  try {
    await api.delete(`/api/coins/images/${imageId}`)
    const idx = existingImages.value.findIndex(img => img.id === imageId)
    if (idx !== -1) {
      existingImages.value.splice(idx, 1)
      updateAllPreview()
    }
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
    
    if (coin.images && coin.images.length) {
      existingImages.value = coin.images
      updateAllPreview()
    }
  } catch (e) {
    error.value = 'Ошибка загрузки монеты'
  }
}

const handleSubmit = async () => {
  // Валидация
  if (!form.name || !form.year || !form.country || !form.denomination || !form.estimated_value) {
    error.value = 'Заполните все обязательные поля'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    if (isEdit.value) {
      // При редактировании отправляем JSON (без фото)
      const updateData = {
        name: form.name,
        year: parseInt(form.year),
        country: form.country,
        denomination: form.denomination,
        metal: form.metal,
        condition: form.condition,
        estimated_value: parseFloat(form.estimated_value)
      }
      
      // Добавляем purchase_price только если он есть
      if (form.purchase_price) {
        updateData.purchase_price = parseFloat(form.purchase_price)
      }
      
      console.log('Отправляем данные:', updateData)  // Для отладки
      
      const response = await api.put(`/api/coins/${route.params.id}`, updateData)
      console.log('Ответ сервера:', response.data)
      
      // Отдельно загружаем новые изображения, если есть
      if (newImages.value.length > 0) {
        const formData = new FormData()
        for (const img of newImages.value) {
          formData.append('images', img.file)
        }
        await api.post(`/api/coins/${route.params.id}/images`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }
      
      router.push('/collection')
    } else {
      // При создании отправляем FormData с фото
      const formData = new FormData()
      formData.append('name', form.name)
      formData.append('year', form.year.toString())
      formData.append('country', form.country)
      formData.append('denomination', form.denomination)
      formData.append('metal', form.metal)
      formData.append('condition', form.condition)
      if (form.purchase_price) formData.append('purchase_price', form.purchase_price.toString())
      formData.append('estimated_value', form.estimated_value.toString())
      
      for (const img of newImages.value) {
        formData.append('images', img.file)
      }
      
      await api.post('/api/coins', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      router.push('/collection')
    }
  } catch (e) {
    console.error('Ошибка:', e.response?.data || e.message)
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
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Область загрузки */
.upload-area {
  border: 2px dashed #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
  transition: all 0.2s;
  min-height: 200px;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-area.has-images {
  padding: 12px;
}

.upload-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  cursor: pointer;
}

.upload-empty svg {
  stroke: #94a3b8;
  margin-bottom: 12px;
}

.upload-empty p {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 4px;
}

.upload-empty span {
  color: #94a3b8;
  font-size: 12px;
}

.upload-preview-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: white;
}

.upload-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-preview-label {
  position: absolute;
  bottom: 4px;
  left: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
}

.upload-remove-btn {
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

.upload-remove-btn:hover {
  background: #ef4444;
}

.upload-add-more {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  border: 2px dashed #cbd5e1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.upload-add-more:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-add-more svg {
  stroke: #94a3b8;
  margin-bottom: 4px;
}

.upload-add-more span {
  font-size: 11px;
  color: #64748b;
}

.upload-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 8px;
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

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-alert {
  margin-top: 20px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 30px;
  color: #ef4444;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Тёмная тема */
body.dark-theme .form-container {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .form-header {
  border-color: #334155;
}

body.dark-theme .form-header h1 {
  color: #f1f5f9;
}

body.dark-theme .form-header p {
  color: #94a3b8;
}

body.dark-theme .form-group label {
  color: #cbd5e1;
}

body.dark-theme .form-group input,
body.dark-theme .form-group select {
  background: #0f172a;
  border-color: #334155;
  color: #f1f5f9;
}

body.dark-theme .upload-area {
  background: #0f172a;
  border-color: #334155;
}

body.dark-theme .upload-area:hover {
  background: #1e293b;
  border-color: #3b82f6;
}

body.dark-theme .upload-empty p {
  color: #94a3b8;
}

body.dark-theme .upload-preview-item {
  background: #0f172a;
  border-color: #334155;
}

body.dark-theme .upload-add-more {
  background: #0f172a;
  border-color: #334155;
}

body.dark-theme .upload-add-more:hover {
  background: #1e293b;
  border-color: #3b82f6;
}

body.dark-theme .form-actions {
  border-color: #334155;
}

body.dark-theme .btn-secondary {
  background: #334155;
  color: #f1f5f9;
}

body.dark-theme .btn-secondary:hover {
  background: #475569;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-card {
    padding: 20px;
  }
  
  .form-header {
    padding: 20px;
  }
  
  .upload-preview-grid {
    justify-content: center;
  }
}
</style>