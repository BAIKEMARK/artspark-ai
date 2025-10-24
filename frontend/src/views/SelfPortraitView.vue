<template>
  <section id="self-portrait" class="feature-panel">
    <h2>AI自画像</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="上传你的照片:">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="true"
          :limit="1"
          list-type="picture-card"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>点击上传照片</span>
          </div>
        </el-upload>
      </el-form-item>
      <el-form-item label="选择/输入风格:">
        <el-input
          v-model="style"
          placeholder="例如：迪士尼卡通, 超级英雄, 像素风"
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
          开始变身
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

    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" alt-text="AI自画像" filename="ai-portrait.png" />
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import { Upload } from '@element-plus/icons-vue'

const style = ref('');
const portraitFile = ref(null);

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/self-portrait', { initialResult: { imageUrl: null } });

function handleFileChange(file) {
  portraitFile.value = file.raw;
}

async function generate() {
  if (!portraitFile.value) {
    error.value = '请上传一张你的照片';
    return;
  }
  if (!style.value) {
    error.value = '请输入你想要的风格';
    return;
  }

  try {
    const base64_image = await fileToBase64(portraitFile.value);
    await execute({ base64_image, style_prompt: style.value });
  } catch (e) {
    console.error(e);
  }
}
</script>
<style scoped>
.upload-demo-box {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  width: 100%;
  height: 100%;
  color: var(--el-text-color-secondary);
}
.upload-demo-box span {
  font-size: 13px;
}
</style>