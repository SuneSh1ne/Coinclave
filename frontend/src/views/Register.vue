<template>
  <div class="auth-page">
    <div class="auth-grid">
      <!-- Левая панель -->
      <div class="auth-info">
        <div class="info-content">
          <div class="logo">
            <span class="logo-mark">C</span>
            <span class="logo-text">CoinClave</span>
          </div>
          <h1>Присоединяйтесь к сообществу</h1>
          <p>Создайте аккаунт и начните управлять своей нумизматической коллекцией уже сегодня</p>
          <div class="stats">
            <div class="stat">
              <span class="stat-value">500+</span>
              <span class="stat-label">активных коллекционеров</span>
            </div>
            <div class="stat">
              <span class="stat-value">10K+</span>
              <span class="stat-label">монет в каталоге</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Правая панель с формой регистрации -->
      <div class="auth-form">
        <div class="form-container">
          <div class="form-header">
            <h2>Создать аккаунт</h2>
            <p>Заполните форму для регистрации</p>
          </div>
          
          <form @submit.prevent="handleRegister">
            <div class="form-group">
              <label>Email</label>
              <input 
                type="email" 
                v-model="email" 
                placeholder="example@mail.com"
                :class="{ error: errors.email }"
              >
              <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
            </div>
            
            <div class="form-group">
              <label>Пароль</label>
              <div class="password-wrapper">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  v-model="password" 
                  placeholder="Не менее 6 символов"
                  :class="{ error: errors.password }"
                  @input="checkPasswordStrength"
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
              <div v-if="password" class="strength-meter">
                <div class="strength-bar">
                  <div class="strength-fill" :style="{ width: strengthPercent + '%', background: strengthColor }"></div>
                </div>
                <span class="strength-text" :style="{ color: strengthColor }">{{ strengthText }}</span>
              </div>
              <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
            </div>
            
            <div class="form-group">
              <label>Подтверждение пароля</label>
              <div class="password-wrapper">
                <input 
                  :type="showConfirmPassword ? 'text' : 'password'" 
                  v-model="confirmPassword" 
                  placeholder="Повторите пароль"
                  :class="{ error: errors.confirmPassword }"
                >
                <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
                  <svg v-if="!showConfirmPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <span v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</span>
            </div>
            
            <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>Зарегистрироваться</span>
            </button>
          </form>
          
          <div class="form-footer">
            <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
          </div>
          
          <div v-if="error" class="error-alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const errors = ref({})

const strengthPercent = computed(() => {
  const pwd = password.value
  if (!pwd) return 0
  let strength = 0
  if (pwd.length >= 6) strength += 25
  if (pwd.length >= 10) strength += 25
  if (/[A-Z]/.test(pwd)) strength += 25
  if (/[0-9]/.test(pwd)) strength += 25
  return strength
})

const strengthColor = computed(() => {
  const percent = strengthPercent.value
  if (percent < 30) return '#ef4444'
  if (percent < 60) return '#f59e0b'
  if (percent < 90) return '#3b82f6'
  return '#10b981'
})

const strengthText = computed(() => {
  const percent = strengthPercent.value
  if (percent < 30) return 'Слабый'
  if (percent < 60) return 'Средний'
  if (percent < 90) return 'Хороший'
  return 'Отличный'
})

const checkPasswordStrength = () => {
  errors.value.password = null
}

const validateForm = () => {
  const newErrors = {}
  
  if (!email.value) {
    newErrors.email = 'Введите email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    newErrors.email = 'Введите корректный email'
  }
  
  if (!password.value) {
    newErrors.password = 'Введите пароль'
  } else if (password.value.length < 6) {
    newErrors.password = 'Пароль должен быть не менее 6 символов'
  }
  
  if (password.value !== confirmPassword.value) {
    newErrors.confirmPassword = 'Пароли не совпадают'
  }
  
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const handleRegister = async () => {
  if (!validateForm()) return
  
  loading.value = true
  error.value = ''
  try {
    await authStore.register(email.value, password.value)
    await authStore.login(email.value, password.value)
    localStorage.setItem('userEmail', email.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
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

.stats {
  display: flex;
  gap: 40px;
  padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat {
  text-align: left;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #3b82f6;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
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

.strength-meter {
  margin-top: 8px;
}

.strength-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.strength-text {
  font-size: 10px;
  margin-top: 4px;
  display: block;
}

.btn-full {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  margin-top: 8px;
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

.field-error {
  font-size: 11px;
  color: #ef4444;
  margin-top: 4px;
  display: block;
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