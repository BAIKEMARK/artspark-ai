<template>
  <div class="language-switcher">
    <el-select
      :model-value="currentLocale"
      @change="handleLocaleChange"
      class="locale-select"
      :teleported="false"
    >
      <el-option
        v-for="loc in availableLocales"
        :key="loc.code"
        :label="loc.name"
        :value="loc.code"
      >
        <span class="locale-option">
          <span class="locale-flag">{{ getFlag(loc.code) }}</span>
          <span class="locale-name">{{ loc.name }}</span>
        </span>
      </el-option>
    </el-select>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLocaleStore } from '../stores/locale'
import { storeToRefs } from 'pinia'

const localeStore = useLocaleStore()
const { locale: currentLocale, availableLocales } = storeToRefs(localeStore)

function handleLocaleChange(newLocale) {
  localeStore.setLocale(newLocale)
}

function getFlag(localeCode) {
  const flags = {
    'zh-CN': '🇨🇳',
    'en-US': '🇺🇸'
  }
  return flags[localeCode] || '🌐'
}
</script>

<style scoped>
.language-switcher {
  width: 100%;
}

.locale-select {
  width: 100%;
}

.locale-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.locale-flag {
  font-size: 1.2rem;
}

.locale-name {
  font-size: 0.95rem;
}
</style>
