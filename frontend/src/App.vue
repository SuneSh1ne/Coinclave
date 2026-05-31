<template>
  <div>
    <NavBar />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  document.body.classList.remove('modal-open')
  // Проверяем наличие токена при загрузке
  const token = localStorage.getItem('token')
  if (token && !authStore.isAuthenticated) {
    authStore.isAuthenticated = true
    authStore.token = token
    authStore.fetchUserInfo()
  }
})
</script>