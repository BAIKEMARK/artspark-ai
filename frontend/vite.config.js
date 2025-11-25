import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  envDir: '../',
  plugins: [vue()],
  server: {
    proxy: {
      // 将 /api 的请求代理到 Python 后端
      '/api': {
        target: 'http://localhost:7860',
        changeOrigin: true,
      },
      // 配置代理，将 /dingtalk-api 开头的请求转发到钉钉 Webhook
      '/dingtalk-api': {
        target: 'https://oapi.dingtalk.com', // 钉钉 API 的基础地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/dingtalk-api/, ''),
      },
    }
  }
})

