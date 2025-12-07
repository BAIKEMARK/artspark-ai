<template>
  <el-card v-if="imageUrl" class="result-card" shadow="never">
    <el-image
      :src="imageUrl"
      :alt="altText"
      fit="contain"
      lazy
      :preview-src-list="[imageUrl]"
      hide-on-click-modal
      preview-teleported
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
.result-card {
  margin-top: 20px;
}
.result-content {
  padding: 14px;
  text-align: center;
}
</style>