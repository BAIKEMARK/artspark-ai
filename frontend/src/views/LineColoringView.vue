<template>
  <section id="line-coloring" class="feature-panel">
    <h2>{{ $t('nav.lineColoring') }}</h2>
    <el-form label-position="top" @submit.prevent="generate">
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
      style="margin-top: 20px;"
    />
    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" :alt-text="$t('views.lineColoring.title')" filename="ai-coloring.png" />
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
