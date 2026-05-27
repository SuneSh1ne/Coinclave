import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/users': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/exchange': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/notifications': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})