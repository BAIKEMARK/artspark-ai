import { defineStore } from 'pinia'
import { ref } from 'vue'
import i18n from '../i18n'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'

const STORAGE_KEY = 'art_spark_locale'

export const useLocaleStore = defineStore('locale', () => {
  // Available locales with Element Plus locale objects
  const availableLocales = ref([
    { code: 'zh-CN', name: '中文', elementPlusLocale: zhCn },
    { code: 'en-US', name: 'English', elementPlusLocale: en }
  ])

  // Current locale state
  const locale = ref('zh-CN')

  // Current Element Plus locale (computed based on current locale)
  const currentElementPlusLocale = ref(zhCn)

  /**
   * Load locale from localStorage
   */
  function loadLocale() {
    try {
      const savedLocale = localStorage.getItem(STORAGE_KEY)
      if (savedLocale && availableLocales.value.some(l => l.code === savedLocale)) {
        locale.value = savedLocale
        i18n.global.locale.value = savedLocale
        
        // Update Element Plus locale
        const localeConfig = availableLocales.value.find(l => l.code === savedLocale)
        if (localeConfig && localeConfig.elementPlusLocale) {
          currentElementPlusLocale.value = localeConfig.elementPlusLocale
        }
      }
    } catch (e) {
      console.error('Failed to load locale from localStorage', e)
    }
  }

  /**
   * Set locale and persist to localStorage
   * @param {string} newLocale - The locale code to set (e.g., 'zh-CN', 'en-US')
   */
  function setLocale(newLocale) {
    if (!availableLocales.value.some(l => l.code === newLocale)) {
      console.warn(`Invalid locale: ${newLocale}. Falling back to zh-CN`)
      newLocale = 'zh-CN'
    }

    locale.value = newLocale
    i18n.global.locale.value = newLocale

    // Update Element Plus locale
    const localeConfig = availableLocales.value.find(l => l.code === newLocale)
    if (localeConfig && localeConfig.elementPlusLocale) {
      currentElementPlusLocale.value = localeConfig.elementPlusLocale
    }

    try {
      localStorage.setItem(STORAGE_KEY, newLocale)
    } catch (e) {
      console.error('Failed to save locale to localStorage', e)
    }
  }

  // Load locale on store initialization
  loadLocale()

  return {
    locale,
    availableLocales,
    currentElementPlusLocale,
    setLocale,
    loadLocale
  }
})
