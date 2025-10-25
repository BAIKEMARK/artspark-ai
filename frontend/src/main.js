import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import './styles/element-theme.scss'
import './styles/main.css'
import App from './App.vue'
import '@phosphor-icons/web/bold'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(ElementPlus) // 全局注册 Element Plus
app.mount('#app')