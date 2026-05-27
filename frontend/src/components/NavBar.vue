<template>
  <header class="navbar">
    <div class="navbar-container">
      <router-link to="/" class="logo">
        <span class="logo-mark">C</span>
        <span class="logo-text">Coinclave</span>
      </router-link>
      
      <nav class="nav-menu">
        <router-link to="/" class="nav-item" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2h-5v-7H9v7H4a2 2 0 0 1-2-2z"/>
          </svg>
          <span>Коллекция</span>
        </router-link>
        
        <router-link to="/add" class="nav-item" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>Добавить</span>
        </router-link>
        
        <router-link to="/exchange" class="nav-item exchange" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 2l4 4-4 4M3 12h15M7 2l-4 4 4 4"/>
            <path d="M21 12h-15M17 22l4-4-4-4"/>
          </svg>
          <span>Обмен</span>
        </router-link>
        
        <div class="nav-item notifications" @click="toggleNotifications">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span class="badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
        </div>
        
        <div class="nav-item user" @click="toggleUserMenu">
          <div class="avatar">
            <span>{{ userInitial }}</span>
          </div>
        </div>
      </nav>
    </div>
    
    <!-- Выпадающее меню уведомлений -->
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
               @click="markRead(notif.id)">
            <div class="notification-content">
              <p>{{ notif.content }}</p>
              <span class="time">{{ formatDate(notif.created_at) }}</span>
            </div>
            <div v-if="!notif.is_read" class="unread-indicator"></div>
          </div>
        </div>
      </div>
    </transition>
    
    <!-- Выпадающее меню пользователя -->
    <transition name="dropdown">
      <div v-if="showUserMenu" class="dropdown-panel user-panel" @click.stop>
        <div class="user-info">
          <div class="user-avatar-large">{{ userInitial }}</div>
          <div>
            <p class="user-email">{{ userEmail }}</p>
            <p class="user-stats">{{ totalValue }} ₽</p>
          </div>
        </div>
        <div class="dropdown-divider"></div>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
const totalValue = ref(0)

const userInitial = computed(() => {
  return userEmail.value ? userEmail.value.charAt(0).toUpperCase() : 'U'
})

const fetchUnreadCount = async () => {
  try {
    const res = await api.get('/notifications/unread-count')
    unreadCount.value = res.data.unread_count
  } catch (e) {}
}

const fetchNotifications = async () => {
  try {
    const res = await api.get('/notifications')
    notifications.value = res.data.slice(0, 10)
  } catch (e) {}
}

const fetchTotalValue = async () => {
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
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'только что'
  if (minutes < 60) return `${minutes} мин`
  if (minutes < 1440) return `${Math.floor(minutes / 60)} ч`
  return `${Math.floor(minutes / 1440)} д`
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleClickOutside = (e) => {
  if (!e.target.closest('.notifications') && !e.target.closest('.notifications-panel')) {
    showNotifications.value = false
  }
  if (!e.target.closest('.user') && !e.target.closest('.user-panel')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  fetchUnreadCount()
  fetchTotalValue()
  const interval = setInterval(fetchUnreadCount, 30000)
  document.addEventListener('click', handleClickOutside)
  
  onUnmounted(() => {
    clearInterval(interval)
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

.text-btn:hover {
  text-decoration: underline;
}

.dropdown-body {
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
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
  width: 260px;
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

.user-email {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
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
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f8fafc;
  color: #ef4444;
}

.dropdown-enter-active, .dropdown-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>