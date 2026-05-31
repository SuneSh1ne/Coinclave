<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="profile-header">
        <h1 class="profile-title">Профиль</h1>
        <p class="profile-subtitle">Управление аккаунтом и настройками</p>
      </div>

      <div class="profile-content">
        <!-- Левая колонка - аватар -->
        <div class="profile-sidebar">
          <div class="avatar-card">
            <div class="avatar-large">{{ userInitial }}</div>
            <h3 class="profile-username">{{ displayName }}</h3>
            <p class="user-email">{{ user.email }}</p>
            <div class="stats-mini">
              <div class="stat-mini">
                <span class="stat-value-mini">{{ userStats.coins_count || 0 }}</span>
                <span class="stat-label-mini">монет</span>
              </div>
              <div class="stat-mini">
                <span class="stat-value-mini">{{ formatPrice(userStats.total_value || 0) }}</span>
                <span class="stat-label-mini">стоимость</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Правая колонка - настройки -->
        <div class="profile-settings">
          <div class="settings-card">
            <h3 class="settings-title">Основная информация</h3>
            
            <div class="form-group">
              <label>Имя пользователя</label>
              <div class="input-with-button">
                <input type="text" v-model="editForm.username" placeholder="Как вас будут видеть другие">
                <button @click="updateUsername" class="btn-secondary" :disabled="loading.username">Сохранить</button>
              </div>
              <p class="form-hint">Будет отображаться другим пользователям</p>
            </div>

            <div class="form-group">
              <label>Email</label>
              <input type="email" :value="user.email" disabled class="disabled-input">
              <p class="form-hint">Email нельзя изменить</p>
            </div>

            <div class="divider"></div>

            <h3 class="settings-title">Внешний вид</h3>
            
            <div class="form-group">
              <label>Тема оформления</label>
              <div class="theme-buttons">
                <button 
                  class="theme-btn" 
                  :class="{ active: editForm.theme === 'light' }"
                  @click="updateTheme('light')"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="5"/>
                    <line x1="12" y1="1" x2="12" y2="3"/>
                    <line x1="12" y1="21" x2="12" y2="23"/>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                    <line x1="1" y1="12" x2="3" y2="12"/>
                    <line x1="21" y1="12" x2="23" y2="12"/>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                  </svg>
                  Светлая
                </button>
                <button 
                  class="theme-btn" 
                  :class="{ active: editForm.theme === 'dark' }"
                  @click="updateTheme('dark')"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                  </svg>
                  Тёмная
                </button>
              </div>
            </div>

            <div class="divider"></div>

            <h3 class="settings-title danger-title">Опасная зона</h3>
            
            <div class="danger-zone">
              <button class="btn-danger" @click="confirmLogout">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                  <polyline points="16 17 21 12 16 7"/>
                  <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                Выйти из аккаунта
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const user = ref({ email: '', username: '', theme: 'light' })
const userStats = ref({})
const loading = ref({ username: false, theme: false })

const editForm = ref({
  username: '',
  theme: 'light'
})

const userInitial = computed(() => {
  const name = user.value.username || user.value.email
  return name ? name.charAt(0).toUpperCase() : 'U'
})

const displayName = computed(() => {
  return user.value.username || (user.value.email ? user.value.email.split('@')[0] : 'Пользователь')
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(Math.round(price || 0))
}

const fetchUserInfo = async () => {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
    editForm.value.username = res.data.username || ''
    editForm.value.theme = res.data.theme || 'light'
    localStorage.setItem('username', res.data.username || '')
    
    if (res.data.theme === 'dark') {
      document.body.classList.add('dark-theme')
      localStorage.setItem('theme', 'dark')
    } else {
      document.body.classList.remove('dark-theme')
      localStorage.setItem('theme', 'light')
    }
  } catch (e) {
    console.error('Ошибка загрузки профиля:', e)
  }
}

const fetchUserStats = async () => {
  if (!user.value.id) return
  try {
    const res = await api.get(`/users/${user.value.id}/stats`)
    userStats.value = res.data
  } catch (e) {
    console.error('Ошибка загрузки статистики:', e)
  }
}

const updateUsername = async () => {
  loading.value.username = true
  try {
    const res = await api.put('/auth/me', { username: editForm.value.username })
    user.value.username = res.data.username
    localStorage.setItem('username', res.data.username || '')
  } catch (e) {
    alert('Ошибка при обновлении имени')
  } finally {
    loading.value.username = false
  }
}

const updateTheme = async (theme) => {
  loading.value.theme = true
  try {
    await api.put('/auth/me', { theme })
    editForm.value.theme = theme
    user.value.theme = theme
    
    localStorage.setItem('theme', theme)
    if (theme === 'dark') {
      document.body.classList.add('dark-theme')
    } else {
      document.body.classList.remove('dark-theme')
    }
  } catch (e) {
    alert('Ошибка при смене темы')
  } finally {
    loading.value.theme = false
  }
}

const confirmLogout = () => {
  if (confirm('Вы уверены, что хотите выйти?')) {
    authStore.logout()
    localStorage.removeItem('username')
    localStorage.removeItem('theme')
    router.push('/')
  }
}

const applySavedTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme')
    editForm.value.theme = 'dark'
  } else {
    document.body.classList.remove('dark-theme')
    editForm.value.theme = 'light'
  }
}

onMounted(() => {
  applySavedTheme()
  fetchUserInfo().then(() => {
    fetchUserStats()
  })
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.profile-header {
  margin-bottom: 32px;
}

.profile-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.profile-subtitle {
  color: #64748b;
  font-size: 14px;
}

.profile-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
}

.profile-sidebar {
  position: sticky;
  top: 100px;
  align-self: start;
}

.avatar-card {
  background: white;
  border-radius: 24px;
  padding: 32px 24px;
  text-align: center;
  border: 1px solid #eef2f6;
}

.avatar-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 700;
  color: white;
  margin: 0 auto 20px;
}

.profile-username {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.user-email {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 20px;
}

.stats-mini {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid #eef2f6;
}

.stat-mini {
  text-align: center;
}

.stat-value-mini {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label-mini {
  font-size: 11px;
  color: #94a3b8;
}

.profile-settings {
  background: white;
  border-radius: 24px;
  border: 1px solid #eef2f6;
  overflow: hidden;
}

.settings-card {
  padding: 28px;
}

.settings-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
}

.danger-title {
  color: #ef4444;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.input-with-button {
  display: flex;
  gap: 12px;
}

.input-with-button input {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
}

.input-with-button input:focus {
  outline: none;
  border-color: #3b82f6;
}

.disabled-input {
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  background: #f8fafc;
  color: #94a3b8;
  width: 100%;
}

.form-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 6px;
}

.divider {
  height: 1px;
  background: #eef2f6;
  margin: 28px 0;
}

.theme-buttons {
  display: flex;
  gap: 12px;
}

.theme-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  color: #475569;
}

.theme-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.theme-btn.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #3b82f6;
}

.danger-zone {
  background: #fef2f2;
  border-radius: 16px;
  padding: 20px;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ef4444;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-secondary {
  padding: 10px 20px;
  background: #f1f5f9;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 13px;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Тёмная тема */
body.dark-theme .profile-page {
  background: #0f172a;
}

body.dark-theme .profile-title {
  color: #f1f5f9;
}

body.dark-theme .profile-subtitle {
  color: #94a3b8;
}

body.dark-theme .avatar-card {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .profile-username {
  color: #f1f5f9;
}

body.dark-theme .user-email {
  color: #94a3b8;
}

body.dark-theme .stat-value-mini {
  color: #10b981;
}

body.dark-theme .stat-label-mini {
  color: #94a3b8;
}

body.dark-theme .stats-mini {
  border-color: #334155;
}

body.dark-theme .profile-settings {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .settings-title {
  color: #f1f5f9;
}

body.dark-theme .form-group label {
  color: #cbd5e1;
}

body.dark-theme .input-with-button input,
body.dark-theme .disabled-input {
  background: #0f172a;
  border-color: #334155;
  color: #f1f5f9;
}

body.dark-theme .form-hint {
  color: #94a3b8;
}

body.dark-theme .divider {
  background: #334155;
}

body.dark-theme .theme-btn {
  background: #0f172a;
  border-color: #334155;
  color: #94a3b8;
}

body.dark-theme .theme-btn:hover {
  background: #1e293b;
  border-color: #475569;
}

body.dark-theme .theme-btn.active {
  background: #1e3a5f;
  border-color: #3b82f6;
  color: #3b82f6;
}

body.dark-theme .danger-zone {
  background: #2a1a1a;
  border-color: #7f1a1a;
}

body.dark-theme .btn-secondary {
  background: #334155;
  color: #f1f5f9;
}

body.dark-theme .btn-secondary:hover {
  background: #475569;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  
  .profile-sidebar {
    position: static;
  }
}
</style>