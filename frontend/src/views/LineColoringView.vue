<template>
  <section id="line-coloring" class="feature-panel">
    <h2>AI智能上色</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="上传线稿/简笔画:">
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
            <span>点击上传线稿</span>
          </div>
          </el-upload>
      </el-form-item>
      <el-form-item label="上色风格:">
        <el-input
          v-model="prompt"
          placeholder="例如：水彩画, 明亮的颜色"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%;"
        >
          开始上色
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
    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" alt-text="AI上色作品" filename="ai-coloring.png" />
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import { Upload } from '@element-plus/icons-vue'
import { useUploadLimiter } from '../composables/useUploadLimiter.js';

const prompt = ref('');

const {
  handleChange: handleFileChange,
  handleRemove,
  uploadClass
} = useUploadLimiter();

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/colorize-lineart', { initialResult: { imageUrl: null } });


async function generate() {
  if (!lineartFile.value) {
    error.value = '请上传一张线稿图片';
    return;
  }
  if (!prompt.value) {
    error.value = '请输入上色风格';
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