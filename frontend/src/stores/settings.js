import { defineStore } from 'pinia';
import { reactive, watch } from 'vue';

const STORAGE_KEY = 'art_spark_ai_settings';

export const useSettingsStore = defineStore('settings', () => {
  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEY);
      if (savedSettings) {
        return JSON.parse(savedSettings);
      }
    } catch (e) {
      console.error("Failed to parse settings from localStorage", e);
    }
    return {
      chat_model: 'Qwen/Qwen3-30B-A3B-Instruct-2507',
      vl_model: 'Qwen/Qwen3-VL-8B-Instruct',
      image_model: 'black-forest-labs/FLUX.1-Krea-dev',
      age_range: '6-8岁',
    };
  };

  const aiSettings = reactive(loadSettings());

  watch(
    aiSettings,
    (newSettings) => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings));
      } catch (e) {
        console.error("Failed to save settings to localStorage", e);
      }
    },
    { deep: true }
  );
  return { aiSettings };
});
