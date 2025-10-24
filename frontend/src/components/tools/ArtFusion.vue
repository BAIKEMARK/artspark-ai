<template>
  <section id="art-fusion" class="feature-panel">
    <h2>艺术融合</h2>
    <div class="form-group">
      <label for="fusion-content-input">上传内容图片 (例如：你的宠物):</label>
      <input type="file" id="fusion-content-input" accept="image/*" @change="emit('file-change', $event, 'artFusionContent')" />
      <img id="fusion-content-preview" class="image-preview" :src="previews.artFusionContent" v-show="previews.artFusionContent" alt="内容预览" />
    </div>
    <div class="form-group">
      <label for="fusion-style-input">上传风格图片 (例如：一张星空图):</label>
      <input type="file" id="fusion-style-input" accept="image/*" @change="emit('file-change', $event, 'artFusionStyle')" />
      <img id="fusion-style-preview" class="image-preview" :src="previews.artFusionStyle" v-show="previews.artFusionStyle" alt="风格预览" />
    </div>
    <button id="generate-fusion-btn" class="cta-btn" @click="generate" :disabled="isLoading">开始融合</button>
    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" alt-text="艺术融合作品" filename="art-fusion.png" />
  </section>
</template>

<script setup>
import { useAIApi } from '../../composables/useAIApi.js';
import ImageResult from '../common/ImageResult.vue';

const props = defineProps({
  files: Object,
  previews: Object,
});
const emit = defineEmits(['file-change']);

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/art-fusion', { initialResult: { imageUrl: null } });

async function generate() {
  if (!props.files.artFusionContent) { error.value = '请上传内容图片'; return; }
  if (!props.files.artFusionStyle) { error.value = '请上传风格图片'; return; }

  try {
    const content_image = await fileToBase64(props.files.artFusionContent);
    const style_image = await fileToBase64(props.files.artFusionStyle);
    await execute({ content_image, style_image });
  } catch (e) {
  }
}
</script>
