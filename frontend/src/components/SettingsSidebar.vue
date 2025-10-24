<template>
  <div>
    <div class="settings-overlay" :class="{ active: isOpen }" @click="$emit('close')"></div>
    <aside id="settings-sidebar" class="settings-sidebar" :class="{ active: isOpen }">
      <div class="settings-sidebar-header">
        <h3><i class="icon ph-bold ph-gear"></i> AI模型设置</h3>
        <button id="settings-close-btn" class="settings-close-btn" aria-label="关闭设置" @click="$emit('close')">
          <i class="icon ph-bold ph-x"></i>
        </button>
      </div>
      <div class="settings-sidebar-content">
        <div class="form-group-sidebar">
          <label for="settings-sidebar-chat-model">对话模型:</label>
          <select id="settings-sidebar-chat-model" :value="aiSettings.chat_model" @input="updateSetting('chat_model', $event.target.value)">
            <option value="Qwen/Qwen3-30B-A3B-Instruct-2507">Qwen3-30B (推荐)</option>
            <option value="Qwen/Qwen3-32B">Qwen/Qwen3-32B</option>
            <option value="Qwen/Qwen3-235B-A22B-Instruct-2507">Qwen3-235B</option>
            <option value="deepseek-ai/DeepSeek-V3.2-Exp">Deepseek-V3.2</option>
          </select>
        </div>
        <div class="form-group-sidebar">
          <label for="settings-sidebar-vl-model">识图模型:</label>
          <select id="settings-sidebar-vl-model" :value="aiSettings.vl_model" @input="updateSetting('vl_model', $event.target.value)">
            <option value="Qwen/Qwen3-VL-8B-Instruct">Qwen-VL-8B (推荐)</option>
            <option value="Qwen/Qwen3-VL-30B-A3B-Instruct">Qwen3-VL-30B</option>
          </select>
        </div>
        <div class="form-group-sidebar">
          <label for="settings-sidebar-image-model">绘图模型:</label>
          <select id="settings-sidebar-image-model" :value="aiSettings.image_model" @input="updateSetting('image_model', $event.target.value)">
            <option value="black-forest-labs/FLUX.1-Krea-dev">FLUX.1-Krea (推荐)</option>
            <option value="MusePublic/489_ckpt_FLUX_1">FLUX.1-dev</option>
            <option value="MusePublic/Qwen-image">Qwen-image</option>
          </select>
        </div>
        <div class="form-group-sidebar">
          <label for="settings-sidebar-age-range">学生年龄:</label>
          <select id="settings-sidebar-age-range" :value="aiSettings.age_range" @input="updateSetting('age_range', $event.target.value)">
            <option value="6-8岁">6-8岁 (低年级)</option>
            <option value="9-10岁">9-10岁 (中年级)</option>
            <option value="11-12岁">11-12岁 (高年级)</option>
            <option value="13-16岁">13-16岁 (初中)</option>
            <option value="17-18岁">17-18岁 (高中)</option>
          </select>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../stores/settings.js';
import { storeToRefs } from 'pinia';

// 1. 定义 props，只接收 isOpen
const props = defineProps({
  isOpen: Boolean,
});

// 2. 定义 emits，只发送 close
const emit = defineEmits(['close']);

// 3. 导入 settings store
const settingsStore = useSettingsStore();

// 4. 从 store 中获取 aiSettings (使用 storeToRefs 保持响应性)
const { aiSettings } = storeToRefs(settingsStore);

// 5. 更新 updateSetting 函数，使其直接调用 store 的 action
function updateSetting(key, value) {
  // 创建一个新对象来更新 store
  const newSettings = { ...aiSettings.value, [key]: value };
  settingsStore.updateSettings(newSettings);
}
</script>
