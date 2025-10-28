import { defineStore } from 'pinia';
import { reactive, watch } from 'vue';

const STORAGE_KEY = 'art_spark_ai_settings';

export const useSettingsStore = defineStore('settings', () => {
  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEY);
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        return {
          chat_model: parsed.chat_model || 'Qwen/Qwen3-30B-A3B-Instruct-2507',
          vl_model: parsed.vl_model || 'Qwen/Qwen3-VL-8B-Instruct',
          image_model: parsed.image_model || 'black-forest-labs/FLUX.1-Krea-dev',
          age_range: parsed.age_range || '6-8岁',
          api_platform: parsed.api_platform || 'modelscope',
          bailian_api_key: parsed.bailian_api_key || '',
          ds_llm_id: parsed.ds_llm_id || 'qwen-plus',
        };
      }
    } catch (e) {
      console.error("Failed to parse settings from localStorage", e);
    }
    return {
      chat_model: 'Qwen/Qwen3-30B-A3B-Instruct-2507',
      vl_model: 'Qwen/Qwen3-VL-8B-Instruct',
      image_model: 'black-forest-labs/FLUX.1-Krea-dev',
      age_range: '6-8岁',
      api_platform: 'modelscope',
      bailian_api_key: '',
      ds_llm_id: 'qwen-plus',
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
