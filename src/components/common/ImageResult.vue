<template>
  <div class="result-container" v-if="imageUrl">
    <img :src="imageUrl" :alt="altText" />
    <a :href="downloadUrl" class="download-btn" :download="filename" target="_blank" rel="noopener noreferrer">
      <i class="icon ph-bold ph-download-simple"></i> 下载图片
    </a>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  imageUrl: String,
  altText: { type: String, default: 'AI 生成作品' },
  filename: { type: String, default: 'art-ai-image.png' },
});

const downloadUrl = computed(() => {
  // Vite 代理会自动处理 /api 前缀
  return `/api/proxy-download?url=${encodeURIComponent(props.imageUrl)}`;
});
</script>

