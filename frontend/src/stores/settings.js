import { defineStore } from 'pinia';
import { reactive } from 'vue';

export const useSettingsStore = defineStore('settings', () => {
  const aiSettings = reactive({
    chat_model: 'Qwen/Qwen3-30B-A3B-Instruct-2507',
    vl_model: 'Qwen/Qwen3-VL-8B-Instruct',
    image_model: 'black-forest-labs/FLUX.1-Krea-dev',
    age_range: '6-8岁',
  });

  function updateSettings(newSettings) {
    Object.assign(aiSettings, newSettings);
  }

  return { aiSettings, updateSettings };
});
