<template>
  <section id="art-fusion" class="feature-panel">
    <h2>艺术融合</h2>
    <el-form label-position="top" @submit.prevent="generate">
      <el-form-item label="上传内容图片 (例如：你的宠物):">
        <el-upload
          action="#"
          :auto-upload="false"
          :on-change="handleContentFileChange"
          :on-remove="handleContentFileRemove"
          :limit="1"
          list-type="picture-card"
          :class="contentUploadClass"
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
          :on-remove="handleStyleFileRemove"
          :limit="1"
          list-type="picture-card"
          :class="styleUploadClass"
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
import { useUploadLimiter } from '../composables/useUploadLimiter.js';

// 1. 为 "内容图片" 调用
const {
  file: contentFile,
  handleChange: handleContentFileChange,
  handleRemove: handleContentFileRemove,
  uploadClass: contentUploadClass
} = useUploadLimiter();

// 2. 为 "风格图片" 调用
const {
  file: styleFile,
  handleChange: handleStyleFileChange,
  handleRemove: handleStyleFileRemove,
  uploadClass: styleUploadClass
} = useUploadLimiter();

const { isLoading, error, result, execute, fileToBase64 } = useAIApi('/api/art-fusion', { initialResult: { imageUrl: null } });

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