<template>
  <section id="art-fusion" class="feature-panel">
    <h2>艺术融合</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="上传内容图片 (例如：你的宠物):">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleContentFileChange"
          :limit="1"
          list-type="picture-card"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>点击上传内容图</span>
          </div>
        </el-upload>
      </el-form-item>
      <el-form-item label="上传风格图片 (例如：一张星空图):">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleStyleFileChange"
          :limit="1"
          list-type="picture-card"
        >
          <div class="upload-demo-box">
            <el-icon :size="28"><Upload /></el-icon>
            <span>点击上传风格图</span>
          </div>
        </el-upload>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="generate"
          :loading="isLoading"
          style="width: 100%;"
        >
          开始融合
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

    <ImageResult v-if="result?.imageUrl" :image-url="result.imageUrl" alt-text="艺术融合作品" filename="art-fusion.png" />
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useAIApi } from '../composables/useAIApi.js';
import ImageResult from '../components/ImageResult.vue';
import { Upload } from '@element-plus/icons-vue'

const contentFile = ref(null);
const styleFile = ref(null);

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/art-fusion', { initialResult: { imageUrl: null } });

function handleContentFileChange(file) {
  contentFile.value = file.raw;
}

function handleStyleFileChange(file) {
  styleFile.value = file.raw;
}

async function generate() {
  if (!contentFile.value) {
    error.value = '请上传内容图片';
    return;
  }
  if (!styleFile.value) {
    error.value = '请上传风格图片';
    return;
  }

  try {
    const content_image = await fileToBase64(contentFile.value);
    const style_image = await fileToBase64(styleFile.value);
    await execute({ content_image, style_image });
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