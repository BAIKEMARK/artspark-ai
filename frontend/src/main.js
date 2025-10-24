import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './styles/main.css'
import App from './App.vue'
import '@phosphor-icons/web/bold' // 使用 bold 图标集

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')