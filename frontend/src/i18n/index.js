import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: 'zh-CN', // Default locale
  fallbackLocale: 'zh-CN', // Fallback locale
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  },
  globalInjection: true // Enable global $t
})

export default i18n
