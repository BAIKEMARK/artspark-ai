import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'
import './styles/element-theme.scss'
import './styles/main.css'
import App from './App.vue'
import '@phosphor-icons/web/bold'
import i18n from './i18n'

const app = createApp(App)
const pinia = createPinia()

// Element Plus locale configuration will be set dynamically in App.vue
app.use(pinia)
app.use(i18n)
app.use(ElementPlus) // 全局注册 Element Plus
app.mount('#app')

// Export locale packages for use in components
export { zhCn, en }