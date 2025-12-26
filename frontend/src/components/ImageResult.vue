<template>
  <div v-if="imageUrl" class="result-container">
    <el-card class="result-card" shadow="never">
      <el-image
        :src="imageUrl"
        :alt="altText"
        fit="contain"
        lazy
        :preview-src-list="[imageUrl]"
        hide-on-click-modal
        preview-teleported
        class="result-image"
      />
      <div class="result-content">
        <el-button
          type="primary"
          plain
          size="small"
          @click="downloadImage"
        >
          <i class="icon ph-bold ph-download-simple"></i> {{ $t('common.download') }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue';

import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  imageUrl: String,
  altText: { type: String, default: '' },
  filename: { type: String, default: 'art-ai-image.png' },
});

const downloadUrl = computed(() => {
  // Vite 代理会自动处理 /api 前缀
  return `/api/proxy-download?url=${encodeURIComponent(props.imageUrl)}`;
});

function downloadImage() {
  const link = document.createElement('a');
  link.href = downloadUrl.value;
  link.download = props.filename;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
</script>

<style scoped>
.result-container {
  text-align: center; /* 让内部的 inline-block 元素居中 */
  margin-top: 20px;
}

.result-card {
  display: inline-block; /* 让卡片宽度贴合内容 */
  max-width: 100%; /* 确保不超出容器 */
  text-align: left; /* 重置内部文本对齐 */
}

.result-image {
  max-width: 100%;
  width: auto;
  height: auto;
  max-height: 600px;
  display: block;
  margin: 0 auto;
}

/* 确保 el-image 内部的 img 标签也能正确缩放 */
.result-image :deep(.el-image__inner) {
  max-width: 100%;
  max-height: 600px;
  width: auto !important;
  height: auto !important;
  object-fit: contain;
}

.result-content {
  padding: 14px;
  text-align: center;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .result-image {
    max-height: 400px;
    max-width: 100%;
  }
  
  .result-image :deep(.el-image__inner) {
    max-height: 400px;
    max-width: 100%;
  }
}
</style>