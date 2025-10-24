<template>
  <section id="self-portrait" class="feature-panel">
    <h2>AI自画像</h2>
    <div class="form-group">
      <label for="portrait-file-input">上传你的照片:</label>
      <input type="file" id="portrait-file-input" accept="image/*" @change="emit('file-change', $event, 'selfPortrait')" />
      <img id="portrait-preview" class="image-preview" :src="previews.selfPortrait" v-show="previews.selfPortrait" alt="照片预览" />
    </div>
    <div class="form-group">
      <label for="portrait-style-input">选择/输入风格:</label>
      <input type="text" id="portrait-style-input" placeholder="例如：迪士尼卡通, 超级英雄, 像素风" v-model="style" />
    </div>
    <button id="generate-portrait-btn" class="cta-btn" @click="generate" :disabled="isLoading">开始变身</button>
    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" alt-text="AI自画像" filename="ai-portrait.png" />
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../../composables/useAIApi.js';
import ImageResult from '../common/ImageResult.vue';

const props = defineProps({
  aiSettings: Object,
  files: Object,
  previews: Object,
});
const emit = defineEmits(['file-change', 'show-api-key-modal']);

const style = ref('');
const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/self-portrait', { initialResult: { imageUrl: null } });

async function generate() {
  if (!props.files.selfPortrait) { error.value = '请上传一张你的照片'; return; }
  if (!style.value) { error.value = '请输入你想要的风格'; return; }

  try {
    const base64_image = await fileToBase64(props.files.selfPortrait);
    await execute({ base64_image, style_prompt: style.value }, props.aiSettings);
  } catch (e) {
    if (e.message === 'unauthorized') {
      emit('show-api-key-modal', 'expired');
    }
  }
}
</script>

