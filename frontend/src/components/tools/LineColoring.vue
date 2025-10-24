<template>
  <section id="line-coloring" class="feature-panel">
    <h2>AI智能上色</h2>
    <div class="form-group">
      <label for="coloring-file-input">上传线稿/简笔画:</label>
      <input type="file" id="coloring-file-input" accept="image/*" @change="emit('file-change', $event, 'coloring')" />
      <img id="coloring-preview" class="image-preview" :src="previews.coloring" v-show="previews.coloring" alt="线稿预览" />
    </div>
    <div class="form-group">
      <label for="coloring-prompt-input">上色风格:</label>
      <input type="text" id="coloring-prompt-input" placeholder="例如：水彩画, 明亮的颜色" v-model="prompt" />
    </div>
    <button id="generate-coloring-btn" class="cta-btn" @click="generate" :disabled="isLoading">开始上色</button>
    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" alt-text="AI上色作品" filename="ai-coloring.png" />
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../../composables/useAIApi.js';
import ImageResult from '../common/ImageResult.vue';
import { useSettingsStore } from '../../stores/settings.js';
import { storeToRefs } from 'pinia';

const props = defineProps({
  files: Object,
  previews: Object,
});
const emit = defineEmits(['file-change']);

const settingsStore = useSettingsStore();
const { aiSettings } = storeToRefs(settingsStore);

const prompt = ref('');
const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/colorize-lineart', { initialResult: { imageUrl: null } });

async function generate() {
  if (!props.files.coloring) { error.value = '请上传一张线稿图片'; return; }
  if (!prompt.value) { error.value = '请输入上色风格'; return; }

  try {
    const base64_image = await fileToBase64(props.files.coloring);
    await execute({ base64_image, prompt: prompt.value });
  } catch (e) {
    // Error handling is now done in useAIApi
  }
}
</script>
