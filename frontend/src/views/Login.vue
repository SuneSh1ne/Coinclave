<template>
  <div class="auth-page">
    <div class="auth-grid">
      <!-- Левая панель с информацией -->
      <div class="auth-info">
        <div class="info-content">
          <div class="logo">
            <span class="logo-mark">C</span>
            <span class="logo-text">Coinclave</span>
          </div>
          <h1>Управление нумизматической коллекцией</h1>
          <p>Систематизируйте свои монеты, отслеживайте стоимость и обменивайтесь с другими коллекционерами</p>
          <div class="features">
            <div class="feature">
              <div class="feature-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
              </div>
              <div>
                <h4>Учёт коллекции</h4>
                <p>Добавляйте монеты с фотографиями и детальными характеристиками</p>
              </div>
            </div>
            <div class="feature">
              <div class="feature-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.66 0 3-4 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4-3-9s1.34-9 3-9"/>
                </svg>
              </div>
              <div>
                <h4>Обмен монетами</h4>
                <p>Находите интересные экземпляры у других пользователей</p>
              </div>
            </div>
            <div class="feature">
              <div class="feature-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="1" x2="12" y2="23"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <div>
                <h4>Оценка стоимости</h4>
                <p>Автоматический расчёт общей ценности вашей коллекции</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Правая панель с формой входа -->
      <div class="auth-form">
        <div class="form-container">
          <div class="form-header">
            <h2>Вход в аккаунт</h2>
            <p>Введите свои данные для доступа к коллекции</p>
          </div>
          
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label>Email</label>
              <input 
                type="email" 
                v-model="email" 
                placeholder="example@mail.com"
                :class="{ error: error }"
                autocomplete="email"
              >
            </div>
            
            <div class="form-group">
              <label>Пароль</label>
              <div class="password-wrapper">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  v-model="password" 
                  placeholder="••••••••"
                  :class="{ error: error }"
                  @keyup.enter="handleLogin"
                >
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
            </div>
            
            <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>Войти</span>
            </button>
          </form>
          
          <div class="form-footer">
            <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
          </div>
          
          <div v-if="error" class="error-alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" fill="none" stroke="#ef4444" stroke-width="2"/>
              <rect x="10.5" y="6" width="3" height="9" rx="1.5" fill="#ef4444"/>
              <circle cx="12" cy="18" r="1.5" fill="#ef4444"/>
            </svg>
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(email.value, password.value)
    localStorage.setItem('userEmail', email.value)
    router.push('/')
  } catch (e) {
    error.value = 'Неверный email или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  background: #f8fafc;
}

.auth-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
}

/* Левая панель */
.auth-info {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.info-content {
  max-width: 440px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;
}

.logo-mark {
  width: 40px;
  height: 40px;
  background: #3b82f6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
}

.logo-text {
  font-size: 22px;
  font-weight: 600;
}

.auth-info h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.3;
}

.auth-info > p {
  font-size: 16px;
  color: #94a3b8;
  margin-bottom: 48px;
  line-height: 1.5;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.feature-icon {
  width: 40px;
  height: 40px;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.feature h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.feature p {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.4;
}

/* Правая панель */
.auth-form {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: white;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.form-header p {
  color: #64748b;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 13px;
  color: #475569;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input.error {
  border-color: #ef4444;
}

.password-wrapper {
  position: relative;
}

.password-wrapper input {
  padding-right: 44px;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 4px;
  display: flex;
  align-items: center;
}

.toggle-password:hover {
  color: #64748b;
}

.btn-full {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  margin-top: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: #64748b;
}

.form-footer a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
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

@media (max-width: 768px) {
  .auth-grid {
    grid-template-columns: 1fr;
  }
  
  .auth-info {
    display: none;
  }
  
  .auth-form {
    padding: 32px 24px;
  }
}
</style>