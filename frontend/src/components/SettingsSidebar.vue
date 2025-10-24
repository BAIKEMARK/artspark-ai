<template>
  <el-drawer
    :model-value="isOpen"
    title="AI模型设置"
    direction="rtl"
    @update:modelValue="$emit('close')"
    size="320px"
  >
    <div class="settings-content">
      <el-form label-position="top">
        <el-form-item label="对话模型:">
          <el-select v-model="aiSettings.chat_model" placeholder="请选择" style="width: 100%;">
            <el-option label="Qwen3-30B (推荐)" value="Qwen/Qwen3-30B-A3B-Instruct-2507" />
            <el-option label="Qwen/Qwen3-32B" value="Qwen/Qwen3-32B" />
            <el-option label="Qwen3-235B" value="Qwen/Qwen3-235B-A22B-Instruct-2507" />
            <el-option label="Deepseek-V3.2" value="deepseek-ai/DeepSeek-V3.2-Exp" />
          </el-select>
        </el-form-item>
        <el-form-item label="识图模型:">
          <el-select v-model="aiSettings.vl_model" placeholder="请选择" style="width: 100%;">
            <el-option label="Qwen-VL-8B (推荐)" value="Qwen/Qwen3-VL-8B-Instruct" />
            <el-option label="Qwen3-VL-30B" value="Qwen/Qwen3-VL-30B-A3B-Instruct" />
          </el-select>
        </el-form-item>
        <el-form-item label="绘图模型:">
          <el-select v-model="aiSettings.image_model" placeholder="请选择" style="width: 100%;">
            <el-option label="FLUX.1-Krea (推荐)" value="black-forest-labs/FLUX.1-Krea-dev" />
            <el-option label="FLUX.1-dev" value="MusePublic/489_ckpt_FLUX_1" />
            <el-option label="Qwen-image" value="MusePublic/Qwen-image" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生年龄:">
          <el-select v-model="aiSettings.age_range" placeholder="请选择" style="width: 100%;">
            <el-option label="6-8岁 (低年级)" value="6-8岁" />
            <el-option label="9-10岁 (中年级)" value="9-10岁" />
            <el-option label="11-12岁 (高年级)" value="11-12岁" />
            <el-option label="13-16岁 (初中)" value="13-16岁" />
            <el-option label="17-18岁 (高中)" value="17-18岁" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
  </el-drawer>
</template>

<script setup>
import { useSettingsStore } from '../stores/settings';
import { storeToRefs } from 'pinia';
import { watch } from 'vue';

const props = defineProps({
  isOpen: Boolean,
});

defineEmits(['close']);

const settingsStore = useSettingsStore();
const { aiSettings } = storeToRefs(settingsStore);

// 使用 watch 来监听 aiSettings 的变化并调用 action
watch(
  aiSettings,
  (newSettings) => {
    settingsStore.updateSettings(newSettings);
  },
  { deep: true } // deep watch 确保对象内部属性的变化也能被监听到
);
</script>

<style scoped>
.settings-content {
  padding: 0 20px;
}
</style>
