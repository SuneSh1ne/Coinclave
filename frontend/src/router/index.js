import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Collection from '../views/Collection.vue'
import CoinDetail from '../views/CoinDetail.vue'
import CoinForm from '../views/CoinForm.vue'
import Exchange from '../views/Exchange.vue'
import UserCollection from '../views/UserCollection.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  { path: '/', name: 'Collection', component: Collection, meta: { requiresAuth: true } },
  { path: '/coin/:id', name: 'CoinDetail', component: CoinDetail, meta: { requiresAuth: true } },
  { path: '/add', name: 'AddCoin', component: CoinForm, meta: { requiresAuth: true } },
  { path: '/coin/:id/edit', name: 'EditCoin', component: CoinForm, meta: { requiresAuth: true } },
  { path: '/exchange', name: 'Exchange', component: Exchange, meta: { requiresAuth: true } },
  { path: '/user/:id', name: 'UserCollection', component: UserCollection, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router