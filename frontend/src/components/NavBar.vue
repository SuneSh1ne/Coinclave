<template>
  <header class="navbar">
    <div class="navbar-container">
      <router-link to="/" class="logo">
        <span class="logo-mark">
          <svg width="36" height="36" viewBox="0 0 60 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Первая монета (золотая) -->
            <circle cx="20" cy="18" r="14" fill="#FBBF24" stroke="#D97706" stroke-width="1.5"/>
            <circle cx="20" cy="18" r="10" fill="#FDE68A" stroke="#D97706" stroke-width="1"/>
            <text x="20" y="23" text-anchor="middle" font-size="11" fill="#D97706" font-weight="bold">$</text>
           
            <!-- Вторая монета (серебряная) -->
            <circle cx="38" cy="26" r="14" fill="#C0C0C0" stroke="#8B7355" stroke-width="1.5"/>
            <circle cx="38" cy="26" r="10" fill="#E8E8E8" stroke="#8B7355" stroke-width="1"/>
            <text x="38" y="31" text-anchor="middle" font-size="11" fill="#8B7355" font-weight="bold">₽</text>
          </svg>
        </span>
        <span class="logo-text">Coinclave</span>
      </router-link>
      
      <nav v-if="!isAuthenticated" class="nav-menu">
        <router-link to="/" class="nav-item" active-class="active">Главная</router-link>
        <router-link to="/login" class="nav-item">Войти</router-link>
        <router-link to="/register" class="nav-item register-btn">Регистрация</router-link>
      </nav>
      
      <nav v-else class="nav-menu">
        <router-link to="/" class="nav-item" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2h-5v-7H9v7H4a2 2 0 0 1-2-2z"/>
          </svg>
          <span>Главная</span>
        </router-link>
        
        <router-link to="/collection" class="nav-item" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>Моя коллекция</span>
        </router-link>
        
        <router-link to="/add" class="nav-item" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>Добавить</span>
        </router-link>
        
        <router-link to="/exchange" class="nav-item exchange" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <!-- Стрелка вправо-вверх -->
            <path d="M17 2 L22 7 L17 12" />
            <line x1="22" y1="7" x2="2" y2="7" />
            <!-- Стрелка влево-вниз -->
            <path d="M7 22 L2 17 L7 12" />
            <line x1="2" y1="17" x2="22" y2="17" />
          </svg>
          <span>Обмен</span>
        </router-link>
        
        <div class="nav-item notifications" @click="toggleNotifications">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span class="badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </div>
        
        <div class="nav-item user" @click="toggleUserMenu">
          <div class="avatar">
            <span>{{ userInitial }}</span>
          </div>
        </div>
      </nav>
    </div>
    
    <transition name="dropdown">
      <div v-if="showNotifications" class="dropdown-panel notifications-panel" @click.stop>
        <div class="dropdown-header">
          <h4>Уведомления</h4>
          <button class="text-btn" @click="markAllAsRead">Все прочитаны</button>
        </div>
        <div class="dropdown-body">
          <div v-if="notifications.length === 0" class="empty-state">
            <p>Нет уведомлений</p>
          </div>
          <div v-for="notif in notifications" :key="notif.id" 
               class="notification-item" 
               :class="{ unread: !notif.is_read }"
               @click="handleNotificationClick(notif)">
            <div class="notification-content">
              <p>{{ notif.content }}</p>
              <span class="time">{{ formatDate(notif.created_at) }}</span>
            </div>
            <div v-if="!notif.is_read" class="unread-indicator"></div>
          </div>
        </div>
      </div>
    </transition>
    
    <transition name="dropdown">
      <div v-if="showUserMenu" class="dropdown-panel user-panel" @click.stop>
        <div class="user-info">
          <div class="user-avatar-large">{{ userInitial }}</div>
          <div>
            <p class="user-name">{{ displayName }}</p>
            <p class="user-email">{{ userEmail }}</p>
            <p class="user-stats">{{ totalValue }} ₽</p>
          </div>
        </div>
        <div class="dropdown-divider"></div>
        <router-link to="/profile" class="dropdown-item profile-item" @click="closeUserMenu">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          </svg>
          Профиль и настройки
        </router-link>
        <button class="dropdown-item" @click="handleLogout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Выйти
        </button>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const unreadCount = ref(0)
const showNotifications = ref(false)
const showUserMenu = ref(false)
const notifications = ref([])
const userEmail = ref(localStorage.getItem('userEmail') || '')
const username = ref(localStorage.getItem('username') || '')
const totalValue = ref(0)

const isAuthenticated = computed(() => authStore.isAuthenticated)

const closeUserMenu = () => {
  showUserMenu.value = false
}

// Обработчик клика по уведомлению
const handleNotificationClick = async (notif) => {
  // Отмечаем как прочитанное
  if (!notif.is_read) {
    await markRead(notif.id)
  }
  
  // Закрываем панель уведомлений
  showNotifications.value = false
  
  // Перенаправляем в зависимости от типа уведомления
  if (notif.type === 'exchange_offer' || notif.type === 'offer_accepted' || notif.type === 'offer_rejected') {
    router.push('/exchange')
  } else {
    router.push('/')
  }
}

watch(isAuthenticated, (newVal) => {
  if (newVal) {
    fetchUserInfo()
    fetchTotalValue()
    fetchUnreadCount()
  } else {
    userEmail.value = ''
    username.value = ''
    totalValue.value = 0
    unreadCount.value = 0
    showUserMenu.value = false
    showNotifications.value = false
  }
})

const userInitial = computed(() => {
  const name = username.value || userEmail.value
  return name ? name.charAt(0).toUpperCase() : 'U'
})

const displayName = computed(() => {
  return username.value || (userEmail.value ? userEmail.value.split('@')[0] : 'Пользователь')
})

const fetchUnreadCount = async () => {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/notifications/unread-count')
    unreadCount.value = res.data.unread_count
  } catch (e) {
    console.error('Ошибка загрузки уведомлений:', e)
  }
}

const fetchNotifications = async () => {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/notifications')
    notifications.value = res.data.slice(0, 10)
  } catch (e) {
    console.error('Ошибка загрузки списка уведомлений:', e)
  }
}

const fetchUserInfo = async () => {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/auth/me')
    username.value = res.data.username || ''
    userEmail.value = res.data.email
    localStorage.setItem('username', username.value)
    localStorage.setItem('userEmail', userEmail.value)
  } catch (e) {}
}

const fetchTotalValue = async () => {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/api/coins/stats/total-value')
    totalValue.value = res.data.total_value
  } catch (e) {}
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    fetchNotifications()
  }
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const markRead = async (id) => {
  try {
    await api.put(`/notifications/${id}/read`)
    await fetchNotifications()
    await fetchUnreadCount()
  } catch (e) {}
}

const markAllAsRead = async () => {
  for (const notif of notifications.value) {
    if (!notif.is_read) {
      await api.put(`/notifications/${notif.id}/read`)
    }
  }
  await fetchNotifications()
  await fetchUnreadCount()
}

const formatDate = (date) => {
  const d = new Date(date)
  const offset = d.getTimezoneOffset()
  const localDate = new Date(d.getTime() - offset * 60000)
  
  const now = new Date()
  const diffMs = now - localDate
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

const handleLogout = () => {
  showUserMenu.value = false
  showNotifications.value = false
  authStore.logout()
  router.push('/')
}

const handleClickOutside = (e) => {
  if (!e.target.closest('.notifications') && !e.target.closest('.notifications-panel')) {
    showNotifications.value = false
  }
  if (!e.target.closest('.user') && !e.target.closest('.user-panel')) {
    showUserMenu.value = false
  }
}

const applyTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme')
  } else {
    document.body.classList.remove('dark-theme')
  }
}

const watchTheme = () => {
  const observer = new MutationObserver(() => {
    const isDark = document.body.classList.contains('dark-theme')
    localStorage.setItem('theme', isDark ? 'dark' : 'light')
  })
  observer.observe(document.body, { attributes: true, attributeFilter: ['class'] })
}

let intervalId = null

onMounted(() => {
  applyTheme()
  watchTheme()
  
  if (isAuthenticated.value) {
    fetchUserInfo()
    fetchTotalValue()
    fetchUnreadCount()
  }
  
  intervalId = setInterval(() => {
    if (isAuthenticated.value) {
      fetchUnreadCount()
    }
  }, 30000)
  
  document.addEventListener('click', handleClickOutside)
  
  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId)
    document.removeEventListener('click', handleClickOutside)
  })
})
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.logo-mark {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.nav-menu {
  display: flex;
  gap: 8px;
  align-items: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 10px;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  border: none;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.nav-item.active {
  background: #eff6ff;
  color: #3b82f6;
}

.register-btn {
  background: #3b82f6;
  color: white;
  padding: 8px 20px;
}

.register-btn:hover {
  background: #2563eb;
  color: white;
}

.nav-item.exchange.active {
  background: #ecfdf5;
  color: #10b981;
}

.nav-item.user {
  padding: 4px;
}

.avatar {
  width: 32px;
  height: 32px;
  background: #e2e8f0;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: #475569;
}

.notifications {
  position: relative;
}

.badge {
  position: absolute;
  top: 2px;
  right: 6px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.dropdown-panel {
  position: absolute;
  top: 60px;
  right: 24px;
  width: 360px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  z-index: 200;
}

.notifications-panel {
  right: 100px;
}

.dropdown-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dropdown-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.text-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #3b82f6;
  cursor: pointer;
}

.dropdown-body {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 14px 20px;
  border-bottom: 1px solid #f8fafc;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: #eff6ff;
}

.notification-content p {
  margin: 0 0 4px;
  font-size: 13px;
  color: #334155;
  line-height: 1.4;
}

.notification-content .time {
  font-size: 11px;
  color: #94a3b8;
}

.unread-indicator {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

.user-panel {
  width: 280px;
}

.user-info {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  align-items: center;
}

.user-avatar-large {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.user-email {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.user-stats {
  font-size: 12px;
  color: #10b981;
  font-weight: 500;
}

.dropdown-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 13px;
  color: #64748b;
  text-decoration: none;
  transition: background 0.2s;
  border-radius: 0;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.profile-item:hover {
  color: #3b82f6;
}

.dropdown-item:last-child:hover {
  color: #ef4444;
}

.dropdown-enter-active, .dropdown-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

/* Тёмная тема */
body.dark-theme .navbar {
  background: rgba(30, 41, 59, 0.98);
  border-color: #334155;
}

body.dark-theme .logo-text {
  color: #f1f5f9;
}

body.dark-theme .nav-item {
  color: #94a3b8;
}

body.dark-theme .nav-item:hover {
  background: #334155;
  color: #f1f5f9;
}

body.dark-theme .nav-item.active {
  background: #1e3a5f;
  color: #3b82f6;
}

body.dark-theme .register-btn {
  background: #3b82f6;
  color: white;
}

body.dark-theme .register-btn:hover {
  background: #2563eb;
}

body.dark-theme .avatar {
  background: #334155;
  color: #f1f5f9;
}

body.dark-theme .dropdown-panel {
  background: #1e293b;
  border-color: #334155;
}

body.dark-theme .dropdown-header {
  border-color: #334155;
}

body.dark-theme .dropdown-header h4 {
  color: #f1f5f9;
}

body.dark-theme .notification-item {
  border-color: #334155;
}

body.dark-theme .notification-item:hover {
  background: #334155;
}

body.dark-theme .notification-item.unread {
  background: #1e3a5f;
}

body.dark-theme .notification-content p {
  color: #cbd5e1;
}

body.dark-theme .notification-content .time {
  color: #94a3b8;
}

body.dark-theme .user-name {
  color: #f1f5f9;
}

body.dark-theme .dropdown-item {
  color: #94a3b8;
}

body.dark-theme .dropdown-item:hover {
  background: #334155;
}

body.dark-theme .dropdown-item.profile-item:hover {
  color: #3b82f6;
}

body.dark-theme .dropdown-item:last-child:hover {
  color: #ef4444;
}
</style>