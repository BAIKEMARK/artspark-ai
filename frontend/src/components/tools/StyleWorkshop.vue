<template>
  <section id="style-workshop" class="feature-panel">
    <h2>创意风格工坊</h2>
    <div class="form-group">
      <label for="style-select">艺术风格:</label>
      <select id="style-select" v-model="style">
        <option value="梵高">梵高 (后印象派)</option>
        <option value="毕加索">毕加索 (立体主义)</option>
        <option value="水墨画">水墨画 (中国传统)</option>
        <option value="剪纸风格">剪纸风格 (中国民间)</option>
        <option value="水彩画">水彩画 (透明)</option>
      </select>
    </div>
    <div class="form-group">
      <label for="style-file-input">上传草图/图片 (可选):</label>
      <input type="file" id="style-file-input" accept="image/*" @change="emit('file-change', $event, 'styleWorkshop')" />
      <img id="style-preview" class="image-preview" :src="previews.styleWorkshop" v-show="previews.styleWorkshop" alt="草图预览" />
    </div>
    <div class="form-group">
      <label for="style-content-input">内容补充描述 (可选):</label>
      <input type="text" id="style-content-input" placeholder="例如：一只戴帽子的狗" v-model="content" />
    </div>
    <button id="generate-style-btn" class="cta-btn" @click="generate" :disabled="isLoading">开始创作</button>
    <div class="loader" v-if="isLoading"></div>
    <p class="error-message">{{ error }}</p>
    <div id="style-result" class="result-container" v-if="result?.imageUrl">
      <img :src="result.imageUrl" alt="风格画作" />
      <p class="style-desc">{{ result.styleDescription }}</p>
      <a :href="downloadUrl" class="download-btn" download="style-workshop.png" target="_blank" rel="noopener noreferrer">
        <i class="icon ph-bold ph-download-simple"></i> 下载图片
      </a>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAIApi } from '../../composables/useAIApi.js';

const props = defineProps({
  files: Object,
  previews: Object,
});
const emit = defineEmits(['file-change']);

const style = ref('梵高');
const content = ref('');
const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/generate-style', { initialResult: { imageUrl: null, styleDescription: '' } });

const downloadUrl = computed(() => result.value?.imageUrl ? `/api/proxy-download?url=${encodeURIComponent(result.value.imageUrl)}` : '#');

async function generate() {
  if (!content.value && !props.files.styleWorkshop) { error.value = '请输入绘制内容或上传一张草图'; return; }

  try {
    let base64_image = null;
    if (props.files.styleWorkshop) {
      base64_image = await fileToBase64(props.files.styleWorkshop);
    }
    await execute({ content: content.value, style: style.value, base64_image });
  } catch (e) {
  }
}
</script>
