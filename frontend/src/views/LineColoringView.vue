<template>
  <section id="line-coloring" class="page-container">

    <div class="header-section">
      <h2 class="page-title">{{ $t('nav.lineColoring') }}</h2>
      <p class="subtitle">{{ $t('views.lineColoring.subtitle') }}</p>
    </div>

    <div class="content-wrapper">
      <el-form label-position="top" @submit.prevent="generate" class="main-form">
      <el-form-item :label="$t('views.lineColoring.uploadLineart')">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleRemove"
          :show-file-list="true"
          :limit="1"
          list-type="picture-card"
          :class="uploadClass"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>{{ $t('views.lineColoring.uploadButton') }}</span>
          </div>
          </el-upload>
      </el-form-item>
      <el-form-item :label="$t('views.lineColoring.coloringStyle')">
        <el-input
          v-model="prompt"
          :placeholder="$t('views.lineColoring.stylePlaceholder')"
          clearable
        >
           <template #suffix>
            <VoiceInputButton @update:text="handleVoiceInput" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%;"
        >
          {{ $t('views.lineColoring.startColoring') }}
        </el-button>
      </el-form-item>
      </el-form>

      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
        class="error-alert"
      />

      <div v-if="result?.imageUrl" class="result-section">
        <ImageResult 
          :image-url="result.imageUrl" 
          :alt-text="$t('views.lineColoring.title')" 
          filename="ai-coloring.png" 
        />
      </div>
    </div>

  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import { Upload } from '@element-plus/icons-vue'
import { useUploadLimiter } from '../composables/useUploadLimiter.js';
import VoiceInputButton from '../components/VoiceInputButton.vue';

const { t } = useI18n();
const prompt = ref('');

const {
  file: lineartFile,
  handleChange: handleFileChange,
  handleRemove,
  uploadClass
} = useUploadLimiter();

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/colorize-lineart', { initialResult: { imageUrl: null } });

const handleVoiceInput = (text) => {
  prompt.value += text;
};

async function generate() {
  if (!lineartFile.value) {
    error.value = t('views.lineColoring.uploadError');
    return;
  }
  if (!prompt.value) {
    error.value = t('views.lineColoring.styleError');
    return;
  }

  try {
    const base64_image = await fileToBase64(lineartFile.value);
    await execute({ base64_image, prompt: prompt.value });
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
/* --- 布局容器 --- */
.page-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* --- 头部区域 --- */
.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 10px;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 10px;
  border-bottom: none; /* 移除全局 h2 的下划线 */
  font-family: var(--font-serif);
  color: var(--secondary-color);
}

.subtitle {
  color: var(--dark-text);
  font-size: 1rem;
  margin-top: 0;
  font-weight: 500;
  opacity: 0.8;
}

/* --- 内容区域 --- */
.content-wrapper {
  background: white;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-color);
  padding: 40px;
  margin-bottom: 20px;
}

.main-form {
  max-width: 600px;
  margin: 0 auto;
}

.main-form .el-form-item {
  margin-bottom: 25px;
}

.main-form .el-button {
  font-size: 1.1rem;
  padding: 15px 0;
  border-radius: 8px;
  font-weight: 600;
}

/* --- 上传区域样式 --- */
:deep(.el-upload--picture-card), :deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 140px;
  height: 140px;
  border-radius: 12px;
  border: 2px dashed var(--border-color);
  transition: all 0.3s ease;
}

:deep(.el-upload--picture-card:hover) {
  border-color: var(--accent-color);
  background-color: #fffbf0;
}

.upload-demo-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  gap: 8px;
}

.upload-demo-box span {
  font-size: 13px;
  text-align: center;
  line-height: 1.3;
}

/* 隐藏已上传文件的上传框 */
:deep(.upload-limit-reached .el-upload--picture-card) {
  display: none;
}

/* --- 错误提示 --- */
.error-alert {
  margin-top: 30px;
  margin-bottom: 20px;
}

/* --- 结果区域 --- */
.result-section {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
  animation: result-fade-in 0.5s ease;
}

/* --- 动画效果 --- */
@keyframes result-fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --- 移动端适配 --- */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 25px 20px;
    margin: 0 10px 20px 10px;
  }
  
  .page-title {
    font-size: 1.6rem;
  }
  
  .main-form {
    max-width: 100%;
  }
  
  :deep(.el-upload--picture-card), :deep(.el-upload-list--picture-card .el-upload-list__item) {
    width: 120px;
    height: 120px;
  }
}
</style>
