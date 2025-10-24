import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 将 /api 的请求代理到 Python 后端
      '/api': {
        target: 'http://localhost:7860',
        changeOrigin: true,
      },
    }
  }
})

