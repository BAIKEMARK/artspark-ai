import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import './styles/element-theme.scss' // 1. 引入自定义主题
import './styles/main.css'          // 2. 重新引入你原来的主样式表 (这是关键)
import App from './App.vue'
import '@phosphor-icons/web/bold' // 使用 bold 图标集

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(ElementPlus) // 全局注册 Element Plus
app.mount('#app')